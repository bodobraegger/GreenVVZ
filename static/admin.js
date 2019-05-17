var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
var apiUrl = 'https://greenvvz.ifi.uzh.ch/'
// var apiUrl = 'http://127.0.0.1:8080/'
var secret_key = $('#anchor-admin').data('api-key') || $('#anchor-admin-2').data('api-key')

function whitelist_from_suggestions(module_id, SmObjId, PiqYear, PiqSession, title) {
    
    $.ajax({
        url: `${apiUrl}whitelist/${PiqYear}/${PiqSession}/${SmObjId}?key=${secret_key}`,
        method : 'POST',
        success : function (data) {
            remove_from_suggestions(module_id)
            populate_whitelist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Whitelist hinzugefügt werden')
        }
    })
}
function whitelist_from_blacklist(module_id, SmObjId, PiqYear, PiqSession, title) {
    $.ajax({
        url: `${apiUrl}whitelist/${PiqYear}/${PiqSession}/${SmObjId}?key=${secret_key}`,
        method : 'POST',
        success : function (data) {
            remove_from_blacklist(module_id)
            populate_whitelist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Whitelist hinzugefügt werden')
        }
    })

}
function blacklist_from_suggestions(module_id, SmObjId, PiqYear, PiqSession, title){
    $.ajax({
        url: `${apiUrl}blacklist/${PiqYear}/${PiqSession}/${SmObjId}?key=${secret_key}`,
        method : 'POST',
        success : function (data) {
            remove_from_suggestions(module_id)
            populate_blacklist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Blacklist hinzugefügt werden')
        }
    })
}
function blacklist_from_whitelist(module_id, SmObjId, PiqYear, PiqSession, title){
    $.ajax({
        url: `${apiUrl}blacklist/${PiqYear}/${PiqSession}/${SmObjId}?key=${secret_key}`,
        method : 'POST',
        success : function (data) {
            remove_from_whitelist(module_id);
            populate_blacklist();
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Blacklist hinzugefügt werden');
        }
    })
}
function save_searchterm(){
    var term = $('#searchterm_text').val()
    $.ajax({
        url :  apiUrl+'searchterms?key='+secret_key,
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
function save_module(){
    var SmObjId = $('#whitelist_text').val()
    if($('option:selected') == 'all') {
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[0]
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[1]
    }
    else {
        var PiqYear = $('option:selected').val().split(' ')[0];
        var PiqSession = $('option:selected').val().split(' ')[1];
    }
    $.ajax({
        url: `${apiUrl}whitelist/${PiqYear}/${PiqSession}/${SmObjId}?key=${secret_key}`,
        method : 'POST',
        success : function (data) {
            add_to_whitelist(data.SmObjId, data.PiqYear, data.PiqSession, data.title)
            $('#whitelist_text').val('')
            populate_blacklist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht gespeichert werden')
        }

    })
}
function delete_searchterm(id){
    $.ajax({
        url: apiUrl+'searchterms/'+id+'?key='+secret_key,
        method : 'DELETE',
        success : function (data) {
            remove_from_searchterms(id)
            populate_suggestions()
        },
        error : function (err) {
            alert('Der Suchbegriff konnte nicht gelöscht werden')
        }
    })
}
function delete_blacklisted_module(module_id){
    $.ajax({
        url: `${apiUrl}blacklist/${module_id}?key=${secret_key}`,
        method : 'DELETE',
        success : function (data) {
            remove_from_blacklist(module_id)
            populate_blacklist()
        },
        error : function (err) {
            console.log(err);
            alert('Das Modul konnte nicht gelöscht werden.');
        }
    })
}

function remove_from_whitelist(module_id){
    document.getElementById(`module_${module_id}`).remove()
}
function remove_from_blacklist(module_id){
    document.getElementById(`module_${module_id}`).remove()
}
function remove_from_suggestions(module_id){
    document.getElementById(`module_${module_id}`).remove()
}
function remove_from_searchterms(id){
    var term = $('#searchterms_body').find('#'+id)
    term.remove()
}

function write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title){
    var url = baseUrlVvzUzh+PiqYear+'/'+PiqSession+'/SM/'+SmObjId;
    return `<tr id="module_${module_id}" data-semester="${PiqYear} ${PiqSession}" data-SmObjId="${SmObjId}" class="shown"><td><a target="_blank" href="${url}">${title}</a></td><td>${convert_session_to_string(PiqSession, PiqYear)}</td><td>`
}
function add_to_whitelist(module_id, SmObjId, PiqYear, PiqSession, title){
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title)}<button name="Anzeigen" onclick="blacklist_from_whitelist(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, '${title}')">Verbergen</button></td></tr>`)
    $('#whitelist_body').append(module)
}
function add_to_blacklist(module_id, SmObjId, PiqYear, PiqSession, title){
    var anzeigen_button = `<button name="Anzeigen" onclick="whitelist_from_blacklist(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, '${title}')">Anzeigen</button>`
    var   delete_button = `<button name="Löschen" onclick="delete_blacklisted_module('${module_id}')">Löschen</button>`
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title)}
        ${anzeigen_button}${delete_button}</td></tr>`)
    $('#blacklist_body').append(module)
}
function add_to_suggestions(module_id, SmObjId, PiqYear, PiqSession, title, whitelisted){
    var anzeigen_button=`<button name="Anzeigen" onclick="whitelist_from_blacklist(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, '${title}')"
        ${whitelisted ? 'disabled' : ''}>Anzeigen</button>`
    var verbergen_button=`<button name="Verbergen" onclick="blacklist_from_whitelist(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, '${title}')"
        ${!whitelisted ? 'disabled' : ''}>Verbergen</button>`
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title)}
        ${anzeigen_button}${verbergen_button}</td></tr>`);
    $('#suggestions_body').append(module)
}

function add_to_searchterms(id, term){
    var searchterm = $('<tr id="'+id+'"><td>'+term+'</td><td><button onclick="delete_searchterm('+id+')">Entfernen</button></td></tr>')
    $('#searchterms_body').append(searchterm)
}

function populate_searchterms(){
    var searchterms = $('#searchterms_body')
    $.ajax({
        url: apiUrl+'searchterms',
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

function populate_whitelist(){
    var whitelist = $('#whitelist_body')
    $.ajax({
        url: apiUrl+'whitelist',
        method : 'GET',
        success : function (data) {
            whitelist.empty()
            for (var row in data) {
                // verarbeite daten
                add_to_whitelist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title)
            }
            whitelist.prepend('<tr><td><input type="text" id="whitelist_text" spellcheck="false" placeholder="Modulnummer (8-Stellige Zahl in der URL zum Modul)" style="width: 90%"></td><td colspan="2"><button name="submit_whitelist" style="display: block; width: 100%" type="button" onclick="save_module()">Modul hinzufügen</button></td></tr>')
            ShowSelectedSemester();
        },
        error : function (err) {
            console.log('Whitelist konnte nicht abgerufen werden: '+err)
        }

    })

}

function populate_blacklist(){
    var blacklist = $('#blacklist_body')
    $.ajax({
        url: apiUrl+'blacklist',
        method : 'GET',
        success : function (data) {
            blacklist.empty()
            for (var row in data) {
                add_to_blacklist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title)
            }
            ShowSelectedSemester();
        },
        error : function (err) {
            console.log('Blacklist konnte nicht abgerufen werden: '+err)
        }

    })
}

function populate_suggestions(){
    var suggestions = $('#suggestions_body')
    $.ajax({
        url: apiUrl+'search',
        method : 'GET',
        success : function (data) {
            suggestions.empty()
            for (var row in data) {
                add_to_suggestions(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].whitelisted)
            }
            $('#suggestions_title_th').trigger("click")
            ShowSelectedSemester();
        },
        error : function (err) {
            console.log('Suchvorschläge konnten nicht abgerufen werden: '+err)
        }

    })
}

function convert_session_to_string(session, year){
    if (session == 3){
        return `<span class="semester">HS </span>${year % 100 || ''}`
    }
    if (session == 4){
        return `<span class="semester">FS </span>${year % 100 || ''}`
    }
    else{
        return 'undefiniert'
    }

}

$(document).ready(function () {
    $('#anchor-admin-2').accordion({collapsible:true,heightStyle:'content'})
});