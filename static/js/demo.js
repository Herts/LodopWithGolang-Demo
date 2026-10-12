/* The coordinates correspond to the sample contract in tools/red-dots/resource. */
function CreatePrintPage(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
        throw new Error('无效的合同数据 / Invalid contract data');
    }
    var printer = getLodop();
    if (!printer || typeof printer.PRINT_INITA !== 'function') {
        throw new Error('请安装 LODOP/C-Lodop / Please install LODOP/C-Lodop');
    }
    var borrower = (data.borrowers || [])[0] || {};
    var property = (data.properties || [])[0] || {};
    var spouse = (data.spouses || [])[0] || {};
    var payment = data.paymentDetails || {};
    var fields = [
        [181, 231, data.contractNum],
        [400, 217, borrower.name],
        [453, 162, borrower.idNum],
        [480, 162, borrower.phoneNum],
        [506, 162, borrower.contractEmail],
        [533, 162, borrower.contactAddr],
        [586, 217, spouse.name],
        [639, 162, spouse.idNum],
        [666, 162, property.owner],
        [692, 162, property.location],
        [719, 162, property.area],
        [772, 217, property.value],
        [825, 162, data.loanTotalAmount],
        [851, 162, data.interestRate],
        [878, 162, payment.name],
        [904, 162, payment.bankAcct]
    ];
    printer.PRINT_INITA(0, 0, 794, 1123, '抵押合同');
    printer.SET_PRINT_MODE('CUSTOM_TASK_NAME', '抵押合同');
    printer.SET_SHOW_MODE('BKIMG_WIDTH', '210mm');
    printer.SET_SHOW_MODE('BKIMG_HEIGHT', '297mm');
    fields.forEach(function (field) {
        var value = field[2] == null ? '' : String(field[2]);
        printer.ADD_PRINT_TEXT(field[0], field[1], 100, 20, value);
    });
    return printer;
}
