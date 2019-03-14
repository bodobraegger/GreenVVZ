$(document).ready(function () {
    var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
    //https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/2017/004/SM/50825256
    var root = $('#anchor-public')
    if(root.data("lang") === 'en'){
        var langTitle = 'UZH Courses related to sustainability';
        var langName = 'Name of the course';
        var langSemester = '(FS = Spring Semester, HS=Fall Semester)'
    } else {
        var langTitle = 'Lehrveranstaltungen der UZH mit Nachhaltigkeitsbezug';
        var langName = 'Name der Lehrveranstaltung';
        var langSemester = '(FS = Frühjahressemester, HS = Herbstsemester)'
    }


    $.ajax({
        url : 'https://api.tempestivus.ch/whitelist',
        method : 'GET',
        success : function (data) {
            var table = $("<table></table>")
            table.append('<thead><th colspan="2"><strong>'+langTitle+'</strong></th></thead>')
            var body = $('<tbody></tbody>')
            body.append('<tr><td><strong>'+langName+'</strong></td><td><strong>Semester</strong><br><p>'+langSemester+'</p></td></tr>')
            for (var row in data){
                var url = baseUrlVvzUzh+data[row].PiqYear+'/'+data[row].PiqSession+'/SM/'+data[row].SmObjId
                if (data[row].held_in == 3){
                    var module = $('<tr><td><a href="'+url+'">'+data[row].title+'</a></td><td>HS</td></tr>')
                }else if (data[row].held_in == 4){
                    var module = $('<tr><td><a href="'+url+'">'+data[row].title+'</a></td><td>FS</td></tr>')
                }
                else {
                    var module = $('<tr><td><a href="'+url+'">'+data[row].title+'</a></td><td>FS & HS</td></tr>')
                }
                body.append(module)
            }
            table.append(body)
            root.append(table)
        },
        error : function (err) {
            console.log(err)
        }
    })
});