var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
var apiUrl = 'https://greenvvz.ifi.uzh.ch/'

$(document).ready(function () {
    //https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/2017/004/SM/50825256
    var root = $('#anchor-public')
    if(root.data("lang") === 'en'){
        var langTitle = 'UZH Modules related to sustainability';
        var langName = 'Name of the Module';
        var langSemester = '(FS = Spring Semester, HS=Fall Semester)'
    } else {
        var langTitle = 'Module der UZH mit Nachhaltigkeitsbezug';
        var langName = 'Name des Moduls';
        var langSemester = '(FS = Frühjahressemester, HS = Herbstsemester)'
    }

    $.ajax({
        url : apiUrl+"/modules/whitelist",
        method : 'GET',
        success : function (data) {
            console.log(data)
            var table = $("<table></table>")
            table.append('<thead><th colspan="2"><strong>'+langTitle+'</strong></th></thead>')
            var body = $('<tbody id="whitelist_body"></tbody>')
            body.append('<tr><td><strong>'+langName+'</strong></td><td><strong>Semester</strong><br><p>'+langSemester+'</p></td></tr>')
            for (var row in data){
                var url = baseUrlVvzUzh+data[row].PiqYear+'/'+data[row].PiqSession+'/SM/'+data[row].SmObjId
                var module = $(`
                <tr id="module_${data[row].id}" data-SmObjId="${data[row].SmObjId}" data-semester="${data[row].PiqYear} ${data[row].PiqSession}" class="shown">
                    <td><a target="_blank" href="${url}">${data[row].title}</a></td><td>${convert_session_to_string(data[row].PiqSession, data[row].PiqYear)}</td>
                </tr>`)
                body.append(module)
            }
            table.append(body)
            root.append(table)
            ShowSelectedModules();
        },
        error : function (err) {
            console.log(err)
        }
    })
});

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