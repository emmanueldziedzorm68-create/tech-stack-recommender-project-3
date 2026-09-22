// Embedded into index.html by build_page.py; no network needed.
function recommendLocally(model, inputs, goals = []) {
    const normalize = value => {
        const key = value.trim().toLowerCase().replace(/\s+/g, ' ');
        return Object.hasOwn(model.aliases, key) ? model.aliases[key] : key;
    };
    const skills = [...new Set(inputs.filter(s => s.trim()).map(normalize))].sort();
    if (skills.length < 3) throw Error('Enter at least three different skills. Aliases count as the same skill.');
    const known = skills.filter(s => Object.hasOwn(model.idf, s));
    const unknown = skills.filter(s => !Object.hasOwn(model.idf, s));
    const goalSkills = [...new Set(goals.filter(s => s.trim()).map(normalize))].sort();
    const knownGoals = goalSkills.filter(s => Object.hasOwn(model.idf, s));
    const profileSkills = [...new Set([...known, ...knownGoals])];
    const norm = list => Math.sqrt(list.reduce((sum, s) => sum + model.idf[s] ** 2, 0));
    const profileNorm = norm(profileSkills);
    // Unique skills have equal TF within each vector; that scalar cancels
    // in cosine similarity, leaving this IDF-weighted expression.
    const recommendations = model.roles.map(role => {
        const matched = role.skills.filter(s => known.includes(s));
        const profileMatched = role.skills.filter(s => profileSkills.includes(s));
        const denominator = profileNorm * norm(role.skills);
        const score = denominator ? profileMatched.reduce((sum, s) => sum + model.idf[s] ** 2, 0) / denominator : 0;
        return {...role, score, matched_skills: matched,
            matched_goal_skills: role.skills.filter(s => knownGoals.includes(s)),
            skills_to_explore: role.skills.filter(s => !known.includes(s))};
    }).filter(role => role.score > 0);
    recommendations.sort((a, b) => b.score - a.score || (a.role < b.role ? -1 : a.role > b.role ? 1 : 0));
    return {input_skills: skills, recognized_skills: known, unknown_skills: unknown,
        goal_skills: goalSkills, unknown_goal_skills: goalSkills.filter(s => !Object.hasOwn(model.idf, s)),
        limited_profile: known.length < 3, recommendations: recommendations.slice(0, 3)};
}
