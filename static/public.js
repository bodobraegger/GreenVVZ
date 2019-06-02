import * as admin from './admin.js';
import {ShowSelectedModules} from './filter.js';

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
        url : admin.apiUrl+"/modules/whitelist",
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
                var url = admin.baseUrlVvzUzh+data[row].PiqYear+'/'+data[row].PiqSession+'/SM/'+data[row].SmObjId
                var module = $(`
                <tr id="module_${data[row].id}" data-SmObjId="${data[row].SmObjId}" data-semester="${data[row].PiqYear} ${data[row].PiqSession}" class="shown">
                    <td><a target="_blank" href="${url}">${data[row].title}</a></td><td>${admin.convert_session_to_string(data[row].PiqSession, data[row].PiqYear)}</td>
                </tr>`)
                body.append(module)
            }
            table.append(body)
            root.append(table)
            // show the modules for current semester - defined in filter.js
            ShowSelectedModules();
            admin.populate_studyprograms();
        },
        error : function (err) {
            console.log(err)
        }
    })
});