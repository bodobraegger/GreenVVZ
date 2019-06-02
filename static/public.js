/* REQUIRES admin.js TO BE LOADED BEFOREHAND, FOR apiUrl, baseUrlVvzUzh and ShowSelectedModules() */
$(document).ready(function () {
    var root = $('#anchor-public')
    // if a data-lang tag exists
    if(root.data("lang") === 'en'){
        var langTitle = 'UZH Modules related to sustainability';
        var langName = 'Name of the Module';
        var langSemester = '(FS = Spring Semester, HS=Fall Semester)'
    } else {
        var langTitle = 'Module der UZH mit Nachhaltigkeitsbezug';
        var langName = 'Name des Moduls';
        var langSemester = '(FS = Frühjahressemester, HS = Herbstsemester)'
    }
    // load the whitelist elements into the page, using the anchor-public div
    $.ajax({
        // apiUrl is defined in admin.js
        url : apiUrl+"/modules/whitelist",
        method : 'GET',
        success : function (data) {
            // create a table, 
            var table = $("<table></table>")
            table.append('<thead><th colspan="2"><strong>'+langTitle+'</strong></th></thead>')
            var body = $('<tbody id="whitelist_body"></tbody>')
            body.append('<tr><td><strong>'+langName+'</strong></td><td><strong>Semester</strong><br><p>'+langSemester+'</p></td></tr>')
            // append the modules as rows with proper id, data-SmObjId, data-semester, and a link to the vvz
            for (var row in data){
                // baseUrlVvzUzh is defined in admin.js
                var url = baseUrlVvzUzh+data[row].PiqYear+'/'+data[row].PiqSession+'/SM/'+data[row].SmObjId
                var module = $(`
                <tr id="module_${data[row].id}" data-SmObjId="${data[row].SmObjId}" data-semester="${data[row].PiqYear} ${data[row].PiqSession}" class="shown">
                    <td><a target="_blank" href="${url}">${data[row].title}</a></td><td>${convert_session_to_string(data[row].PiqSession, data[row].PiqYear)}</td>
                </tr>`)
                body.append(module)
            }
            table.append(body)
            root.append(table)
            // show the modules for current semester - defined in admin.js
            ShowSelectedModules();
        },
        error : function (err) {
            console.log(err)
        }
    })
});
/**
 * Convert session to human readable span element as string.
 * @param  {Number} session The session code, either 3, 4, 003, 004.
 * @param  {Number} year the module year data.
 * @return {String} A span containing the humanreadable semester and year.
 */
function convert_session_to_string(session, year){
    if (session == 3){
        return `<span class="semester">HS </span>${year % 100 || ''}`
    }
    if (session == 4){
        return `<span class="semester">FS </span>${(year+1) % 100 || ''}`
    }
    else{
        return 'undefiniert'
    }
}