// Run the actual inline scripts without a backend, including form rendering.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const page = fs.readFileSync('index.html', 'utf8');
const catalogueText = page.match(/<script id="catalogue" type="application\/json">([\s\S]*?)<\/script>/)[1];
const model = JSON.parse(catalogueText);
function element() {
    return {textContent: '', value: '', children: [], hidden: false, disabled: false,
        events: {}, append(...children) { this.children.push(...children); },
        replaceChildren(...children) { this.children = children; },
        addEventListener(name, fn) { this.events[name] = fn; }};
}
const elements = Object.fromEntries(['form','skills','goals','status','results','results-title','submit','vocabulary','catalogue'].map(id => [id,element()]));
elements.catalogue.textContent = catalogueText;
const context = vm.createContext({document: {
    querySelector: selector => elements[selector.slice(1)],
    querySelectorAll: () => [], createElement: element,
}, fetch: () => { throw Error('Standalone page must not make network requests.'); }});
for (const match of page.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
    if (!match[1].includes('application/json')) vm.runInContext(match[2], context);
}
async function submit(skills) {
    elements.skills.value = skills;
    await elements.form.events.submit({preventDefault() {}});
}
(async () => {
    assert(elements.vocabulary.textContent.includes('python'));
    await submit('HTML, CSS, React');
    assert.equal(elements.results.children.length, 3);
    assert.equal(elements.results.children[0].children[1].textContent, 'Full Stack Developer');
    assert.equal(elements.status.textContent, '');
    assert.equal(elements.submit.disabled, false);
    await submit('python');
    assert.match(elements.status.textContent, /at least three/);
    assert.equal(elements.results.children.length, 0);
    await submit('pottery, baking, knitting');
    assert.match(elements.status.textContent, /No matching roles/);
    assert.equal(elements.results.children.length, 0);
    const cases = JSON.parse(fs.readFileSync(0, 'utf8') || '[]');
    for (const sample of cases) {
        const actual = context.recommendLocally(model, sample.skills, sample.goals || []);
        assert.equal(JSON.stringify(actual.recognized_skills), JSON.stringify(sample.expected.recognized_skills));
        assert.equal(JSON.stringify(actual.unknown_skills), JSON.stringify(sample.expected.unknown_skills));
        assert.equal(actual.recommendations.length, sample.expected.recommendations.length);
        actual.recommendations.forEach((role, i) => {
            assert.equal(role.role, sample.expected.recommendations[i].role);
            assert(Math.abs(role.score - sample.expected.recommendations[i].score) < 1e-12);
        });
    }
    console.log('Standalone form checks passed; Python/browser parity passed for '+cases.length+' profiles.');
})().catch(error => { console.error(error); process.exitCode = 1; });
