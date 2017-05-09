/*********************** code block formatting stuff *************************/
/* get string format function if not provided */
String.prototype.formatUnicorn = String.prototype.formatUnicorn ||
function () {
    "use strict";
    var str = this.toString();
    if (arguments.length) {
        var t = typeof arguments[0];
        var key;
        var args = ("string" === t || "number" === t) ?
            Array.prototype.slice.call(arguments)
            : arguments[0];

        for (key in args) {
            str = str.replace(new RegExp("\\{" + key + "\\}", "gi"), args[key]);
        }
    }

    return str;
};
function open_code_block(arg_cbid) {
    var cbs = document.getElementsByClassName('codeblks');
    var specific_cb = document.getElementById('codeblk_' + arg_cbid);
    var imgStr = ("<img id=\"codeblk_opened_img_{cbid}\" class=\"codeblk_img\" onclick=\"hide_code_block('{cbid}')\" "
        + "src=\"../img/code-block-opened.gif\" alt=\"\" />").formatUnicorn({cbid: arg_cbid});
    var completeHtml = imgStr + "<div id=codeblk_{cbid} class=\"innercb\" style='display:block'".formatUnicorn({cbid: arg_cbid})
        + specific_cb.innerHTML + "</div>";
    cbs[arg_cbid].innerHTML = completeHtml;
}

function hide_code_block(arg_cbid) {
    var cbs = document.getElementsByClassName('codeblks');
    var specific_cb = document.getElementById('codeblk_' + arg_cbid);
    var imgStr = ("<div class=\"imgblk\" style=\"display:block\"> "
        + "<img id=\"codeblk_closed_img_{cbid}\" onclick=\"open_code_block('{cbid}')\" "
        + "src=\"../img/code-block-closed.gif\" alt=\"\" />").formatUnicorn({cbid: arg_cbid})
        + "  View Code</div>";
    var completeHtml = imgStr + "<div id=codeblk_{cbid} class=\"innercb\" style='display:none'".formatUnicorn({cbid: arg_cbid})
        + specific_cb.innerHTML + "</div>";
    cbs[arg_cbid].innerHTML = completeHtml;
}

/* at first we hide all those long code snippet */
var cbs = document.getElementsByClassName('codeblks');
for(i=0; i<cbs.length; i++){
    var imgStr = ("<div class=\"imgblk\" style=\"display:block\"> "
        + "<img id=\"codeblk_closed_img_{cbid}\" onclick=\"open_code_block('{cbid}')\" "
        + "src=\"../img/code-block-closed.gif\" alt=\"\" />").formatUnicorn({cbid: i})
        + "  View Code</div>";
    var completeHtml = imgStr + "<div id=codeblk_{cbid} class=\"innercb\" style='display:none'".formatUnicorn({cbid: i})
        + cbs[i].innerHTML + "</div>";
    cbs[i].innerHTML = completeHtml;
}
/**************************** END code block formatting ********************************/

