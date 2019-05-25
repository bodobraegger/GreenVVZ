var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
var apiUrl = 'https://greenvvz.ifi.uzh.ch/'
// var apiUrl = 'http://127.0.0.1:8080/'
var secret_key = $('#anchor-admin').data('api-key') || $('#anchor-admin-2').data('api-key')

async function post_module_to_db(module_id, SmObjId, PiqYear, PiqSession, whitelisted, searchterm) {
    await $.ajax({
        contentType: 'application/json',
        url: `${apiUrl}/modules?key=${secret_key}`,
        method : 'POST',
        data: JSON.stringify({
            'PiqYear': PiqYear,
            'PiqSession': PiqSession,
            'SmObjId': SmObjId,
            'whitelisted': whitelisted,
            'searchterm': searchterm,
        }),
        success : function (data) {
            flag_in_suggestions(module_id, whitelisted)
            populate_whitelist();
            populate_blacklist();
            populate_studyprograms();
        },
        error : function (err) {
            alert(`Das Modul konnte nicht als ${whitelisted ? 'whitelisted' : 'blacklisted'} gespeichert hinzugefügt werden`)
        }
    })
}

async function update_whitelist_status(module_id, whitelisted, SmObjId, PiqYear, PiqSession) {
    await $.ajax({
        url: `${apiUrl}/modules/${module_id}?whitelisted=${whitelisted}&key=${secret_key}`,
        method : 'PUT',
        success : function (data) {
            remove_module(module_id)
            if(whitelisted) populate_whitelist();
            else populate_blacklist();
            populate_suggestions();
            populate_studyprograms();
        },
        error : function (err) {
            alert(`Das Modul konnte nicht als ${whitelisted ? 'whitelisted' : 'blacklisted'} markiert werden`);
        }
    })
}

async function save_searchterm(){
    var term = $('#searchterm_text').val()
    await $.ajax({
        url :  apiUrl+'/searchterms?key='+secret_key,
        method : 'POST',
        dataType : 'json',
        data : {'term':term},
        success : function (data) {
            $('#searchterm_text').val('')
            populate_searchterms()
            populate_suggestions()
        },
        error : function (err) {
            alert('Der Suchbegriff konnte nicht gespeichert werden')
        }

    })
}
async function save_module(){
    var SmObjId = $('#whitelist_text').val()
    if($('option:selected') == 'all') {
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[0]
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[1]
    }
    else {
        var PiqYear = $('option:selected').val().split(' ')[0];
        var PiqSession = $('option:selected').val().split(' ')[1];
    }
    await $.ajax({
        url: `${apiUrl}/modules/?key=${secret_key}`,
        data: {
            'PiqYear': PiqYear,
            'PiqSession': PiqSession,
            'SmObjId': SmObjId,
            'whitelisted': 1,
        },
        method : 'POST',
        success : function (data) {
            add_to_whitelist(data.SmObjId, data.PiqYear, data.PiqSession, data.title, data.searchterm)
            $('#whitelist_text').val('')
            populate_blacklist();
            populate_suggestions();
            populate_studyprograms();
        },
        error : function (err) {
            alert('Das Modul konnte nicht gespeichert werden')
        }

    })
}
async function delete_searchterm(id){
    await $.ajax({
        url: apiUrl+'/searchterms/'+id+'?key='+secret_key,
        method : 'DELETE',
        success : function (data) {
            remove_from_searchterms(id)
            populate_suggestions();
        },
        error : function (err) {
            alert('Der Suchbegriff konnte nicht gelöscht werden')
        }
    })
}
async function delete_blacklisted_module(module_id){
    await $.ajax({
        url: `${apiUrl}/modules/${module_id}?key=${secret_key}`,
        method : 'DELETE',
        success : function (data) {
            remove_module(module_id)
            populate_blacklist();
            populate_suggestions();
            // flag_in_suggestions(module_id, -1); ids won't match!
        },
        error : function (err) {
            console.log(err);
            alert('Das Modul konnte nicht gelöscht werden.');
        }
    })
}

function remove_module(module_id){
    document.getElementById(`module_${module_id}`).remove()
}
function flag_in_suggestions(module_id, whitelisted){
    var button_parent = document.getElementById(`module_${module_id}`).children[3];
    if(whitelisted==1) {
        button_parent.querySelector('button[name="Anzeigen"]').disabled = true;
        button_parent.querySelector('button[name="Verbergen"]').disabled = false;
    }
    else if(whitelisted==0) {
        button_parent.querySelector('button[name="Anzeigen"]').disabled = false;
        button_parent.querySelector('button[name="Verbergen"]').disabled = true;
    }
    else {
        button_parent.querySelector('button[name="Anzeigen"]').disabled = false;
        button_parent.querySelector('button[name="Verbergen"]').disabled = false;
    }
}
function remove_from_searchterms(id){
    var term = $('#searchterms_body').find('#'+id)
    term.remove()
}

function write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var url = baseUrlVvzUzh+PiqYear+'/'+PiqSession+'/SM/'+SmObjId;
    return `<tr id="module_${module_id}" data-SmObjId="${SmObjId}" data-semester="${PiqYear} ${PiqSession}" class="shown">
        <td><a target="_blank" href="${url}">${title}</a></td>
        <td class="searchterm">${searchterm}</td>
        <td>${convert_session_to_string(PiqSession, PiqYear)}</td>
        `
}
function add_to_whitelist(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
        <td><button name="Anzeigen" onclick="update_whitelist_status(${module_id}, 0)">Verbergen</button></td>
    </tr>`)
    $('#whitelist_body').append(module)
}
function add_to_blacklist(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var anzeigen_button = `<button name="Anzeigen" onclick="update_whitelist_status(${module_id}, 1)">Anzeigen</button>`
    var   delete_button = `<button name="Löschen" onclick="delete_blacklisted_module(${module_id})">Löschen</button>`
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
            <td>${anzeigen_button}${delete_button}</td>
        </tr>`)
    $('#blacklist_body').append(module)
}
function add_to_suggestions(module_id, SmObjId, PiqYear, PiqSession, title, whitelisted, searchterm){
    var anzeigen_button=`<button name="Anzeigen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=1, '${searchterm}')"
        ${whitelisted==1 ? 'disabled' : ''}>Anzeigen</button>`
    var verbergen_button=`<button name="Verbergen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=0, '${searchterm}')"
        ${whitelisted==0 ? 'disabled' : ''}>Verbergen</button>`
    var whitelist_status_td = `<td class="whitelist_status whitelisted_${whitelisted}">${whitelisted==1 ? 'Ja' : 'Nein'}</td>`

    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
            <td>${anzeigen_button}${verbergen_button}</td>
            ${whitelist_status_td}
        </tr>`);
    $('#suggestions_body').append(module)
}

function add_to_searchterms(id, term){
    var searchterm = $('<tr id="'+id+'"><td>'+term+'</td><td><button onclick="delete_searchterm('+id+')">Entfernen</button></td></tr>')
    $('#searchterms_body').append(searchterm)
}

async function populate_searchterms(){
    var searchterms = $('#searchterms_body')
    await $.ajax({
        url: apiUrl+'/searchterms',
        method: 'GET',
        success: function (data) {
            searchterms.empty()
            for (var row in data){
                add_to_searchterms(data[row].id, data[row].term)
            }
            searchterms.prepend('<tr><td><input type="text" id="searchterm_text" spellcheck="true" placeholder="Suchbegriff für Titel, Beschrieb oder Kürzel" style="width: 90%"></td><td><button name="submit_searchterm" style="display: block; width: 100%" type="button" onclick="save_searchterm()">Suchbegriff speichern</button></td></tr>')
        }
    })


}

async function populate_whitelist(){
    var whitelist = $('#whitelist_body')
    await $.ajax({
        url: apiUrl+'/modules/whitelist',
        method : 'GET',
        beforeSend: function () { $('#whitelist').find('div.loading').toggle(); },
        success : function (data) {
            whitelist.empty()
            for (var row in data) {
                // verarbeite daten
                add_to_whitelist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].searchterm)
            }
            whitelist.prepend('<tr><td colspan="3"><input type="text" id="whitelist_text" spellcheck="false" placeholder="Modulnummer (8-Stellige Zahl in der URL zum Modul)" style="width: 90%"></td><td><button name="submit_whitelist" style="display: block; width: 100%" type="button" onclick="save_module()">Modul hinzufügen</button></td></tr>')
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Whitelist konnte nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#whitelist').find('div.loading').toggle();
        }

    })

}

async function populate_blacklist(){
    var blacklist = $('#blacklist_body');
    await $.ajax({
        url: apiUrl+'/modules/blacklist',
        method : 'GET',
        beforeSend: function () { $('#blacklist').find('div.loading').toggle(); },
        success : function (data) {
            blacklist.empty()
            for (var row in data) {
                add_to_blacklist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].searchterm)
            }
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Blacklist konnte nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#blacklist').find('div.loading').toggle();
        }
    })
}

async function populate_suggestions(){
    var suggestions = $('#suggestions_body')
    await $.ajax({
        url: apiUrl+'/search',
        method : 'GET',
        beforeSend: function () { $('#suggestions').find('div.loading').toggle(); },
        success : function (data) {
            suggestions.empty()
            console.log(data)
            for (var row in data) {
                add_to_suggestions(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].whitelisted, data[row].searchterm)
            }
            $('#suggestions_title_th').removeClass();
            $('#suggestions_title_th').trigger("click")
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Suchvorschläge konnten nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#suggestions').find('div.loading').toggle();
        }

    })
}

async function populate_studyprograms() {
    await $.ajax({
        url: apiUrl+'/studyprograms',
        method : 'GET',
        beforeSend: function () { $('#suggestions').find('div.loading').toggle(); },
        success : function (data) {
            studyprograms = data;
            studyprogram_textlist = Object.keys(studyprograms).map(function(key){
                return studyprograms[key];
            });
            studyprogram_ids = Object.keys(studyprograms)

        },
        error : function (err) {
            console.log('/studyprograms konnten nicht abgerufen werden: '+err)
        },
    })
    await $.ajax({
        url: apiUrl+'/studyprograms_modules',
        method : 'GET',
        beforeSend: function () { $('#suggestions').find('div.loading').toggle(); },
        success : function (data) {
            studyprogramid_moduleids = data;
        },
        error : function (err) {
            console.log('/studyprograms_modules konnte nicht abgerufen werden: '+err)
        },
    })
    // update the autocomplete list
    autocomplete(document.getElementById("studyprogram_input"), studyprogram_textlist);
}

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

$(document).ready(function () {
    $('#anchor-admin-2').accordion({collapsible:true,heightStyle:'content'})
    ShowSelectedModules();
});