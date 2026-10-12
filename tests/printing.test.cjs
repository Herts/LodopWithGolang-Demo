const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/demo.js'), 'utf8');

function setup(printer) {
    const context = { getLodop: () => printer };
    vm.createContext(context);
    vm.runInContext(source, context);
    return context.CreatePrintPage;
}

test('print template binds sample values and preserves zero', () => {
    const texts = [];
    const printer = {
        PRINT_INITA() {}, SET_PRINT_MODE() {}, SET_SHOW_MODE() {},
        ADD_PRINT_TEXT(...args) { texts.push(args); }
    };
    const create = setup(printer);
    assert.equal(create({ contractNum: 'ABC', borrowers: [{ name: 'Example' }], interestRate: 0 }), printer);
    assert.equal(texts.length, 16);
    assert.deepEqual(texts[0], [181, 231, 100, 20, 'ABC']);
    assert.equal(texts[1][4], 'Example');
    assert.equal(texts[13][4], '0');
    assert.equal(texts[15][4], '');
});

test('missing plugin and invalid data return actionable errors', () => {
    assert.throws(() => setup(null)({}), /install LODOP/);
    assert.throws(() => setup({})({}), /install LODOP/);
    assert.throws(() => setup(null)(null), /Invalid contract data/);
    assert.throws(() => setup(null)([]), /Invalid contract data/);
});

test('plugin install notice preserves the page and uses an available download link', () => {
    let notice;
    const body = { firstChild: null, insertBefore(element) { notice = element; } };
    Object.defineProperty(body, 'innerHTML', {
        set() { throw new Error('Page body must not be replaced'); }
    });
    const context = {
        navigator: { userAgent: 'Chrome/120.0' },
        document: {
            readyState: 'complete', body,
            head: { firstChild: null, insertBefore() {} },
            createElement() { return {}; },
            getElementById() { return notice; }
        },
        alert() { throw new Error('Unexpected alert'); }
    };
    vm.createContext(context);
    const helper = fs.readFileSync(path.join(__dirname, '../static/js/LodopFuncs.js'), 'utf8');
    vm.runInContext(helper, context);
    assert.equal(context.getLodop(), undefined);
    assert.equal(notice.id, 'lodop-notice');
    assert.match(notice.innerHTML, /https:\/\/www\.lodop\.net\/download\.html/);
    assert.doesNotMatch(notice.innerHTML, /\/static\/LODOP\/.*\.exe/);
});
