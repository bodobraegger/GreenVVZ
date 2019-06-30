/* REQUIRES admin.js TO BE LOADED BEFOREHAND, FOR apiUrl, baseUrlVvzUzh and ShowSelectedModules() */
$(document).ready(function () {
    lang=getUrlParam('lang');
    // if a data-lang tag exists
    if(lang == 'en'){
        // global abbreviation to make convert_to_session able to access
        spring_sem_abbr = 'SS';
        spring_sem = 'Spring Semester'
        fall_sem_abbr = 'FS'
        fall_sem = 'Fall Semester'
        var langTitle = 'UZH Modules related to sustainability';
        var langName = 'Name of the Module';
    } else {
        spring_sem_abbr = 'FS';
        spring_sem = 'Frühjahrssemester'
        fall_sem_abbr = 'HS'
        fall_sem = 'Herbstsemester'
        var langTitle = 'Module der UZH mit Nachhaltigkeitsbezug';
        var langName = 'Name des Moduls';
    }
    var langSemester = `${spring_sem_abbr} = ${spring_sem}, ${fall_sem_abbr} = ${fall_sem})`
    // load the whitelist elements into the page, using the anchor-public div
    $.ajax({
        // apiUrl is defined in admin.js
        url : apiUrl+"/modules/whitelist",
        method : 'GET',
        beforeSend : function() {
            // change the semester selector language
            if(lang=="en"){
                $('#studyprogram_input').attr('placeholder', 'Study program');
                $('#all_semesters').html('All semesters');
                $('#studyprogram_btn_clear').html('Delete filter')
                $('#semester_selector option').each(function() {
                    if($(this).attr('value').split(' ')[1].includes('3')) {
                        $(this).html(`${fall_sem} ${$(this).attr('value').split(' ')[0]}`)
                    }
                    else if($(this).attr('value').split(' ')[1].includes('4')) {
                        $(this).html(`${spring_sem} ${$(this).attr('value').split(' ')[0]}`)
                    }
                })
            }
        },
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
            $('#anchor-public').append(table)
            // show the modules for current semester - defined in admin.js
            ShowSelectedModules();
        },
        error : function (err) {
            console.log(err)
        }
    })
});
/**
 * Convert session to human readable span element as string. DIFFERENT FROM admin.js
 * @param  {Number} session The session code, either 3, 4, 003, 004.
 * @param  {Number} year the module year data.
 * @return {String} A span containing the humanreadable semester and year.
 */
function convert_session_to_string(session, year){
    if (session == 3){
        return `<span class="semester">${fall_sem_abbr} </span>${year % 100 || ''}`
    }
    if (session == 4){
        return `<span class="semester">${spring_sem_abbr} </span>${(year+1) % 100 || ''}`
    }
    else{
        return 'undefiniert'
    }
}

function getUrlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	return results[1] || 0;
}