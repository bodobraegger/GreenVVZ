var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
var apiUrl = 'https://greenvvz.ifi.uzh.ch/'
var secret_key = $('#anchor-admin').data('api-key') || $('#anchor-admin-2').data('api-key')

function whitelist_from_suggestions(SmObjId, PiqYear, PiqSession, held_in, title) {
    
    $.ajax({
        url: apiUrl+'whitelist/'+SmObjId+'?key='+secret_key,
        method : 'POST',
        success : function (data) {
            delete_from_suggestions(SmObjId)
            populate_whitelist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Whitelist hinzugefügt werden')
        }
    })
}
function whitelist_from_blacklist(SmObjId, PiqYear, PiqSession, held_in, title) {
    $.ajax({
        url: apiUrl+'whitelist/'+SmObjId+'?key='+secret_key,
        method : 'POST',
        success : function (data) {
            delete_from_blacklist(SmObjId)
            populate_whitelist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Whitelist hinzugefügt werden')
        }
    })

}
function blacklist_from_suggestions(SmObjId, PiqYear, PiqSession, held_in, title){
    $.ajax({
        url: apiUrl+'blacklist/'+SmObjId+'?key='+secret_key,
        method : 'POST',
        success : function (data) {
            delete_from_suggestions(SmObjId)
            populate_blacklist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht zur Blacklist hinzugefügt werden')
        }
    })
}
function blacklist_from_whitelist(SmObjId, PiqYear, PiqSession, held_in, title){
    $.ajax({
        url: apiUrl+'blacklist/'+SmObjId+'?key='+secret_key,
        method : 'POST',
        success : function (data) {
            delete_from_whitelist(SmObjId);
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
    var id = $('#whitelist_text').val()
    $.ajax({
        url :  apiUrl+'whitelist/'+id+'?key='+secret_key,
        method : 'POST',
        success : function (data) {
            add_to_whitelist(data.SmObjId, data.PiqYear, data.PiqSession, data.held_in, data.title)
            $('#whitelist_text').val('')
            populate_blacklist()
        },
        error : function (err) {
            alert('Das Modul konnte nicht gespeichert werden')
        }

    })
}
function remove_searchterm(id){
    $.ajax({
        url: apiUrl+'searchterms/'+id+'?key='+secret_key,
        method : 'DELETE',
        success : function (data) {
            delete_from_searchterms(id)
            populate_suggestions()
        },
        error : function (err) {
            alert('Der Suchbegriff konnte nicht gelöscht werden')
        }
    })
}
function delete_from_whitelist(id){
    $('#whitelist_body').find('#'+id).remove()
}
function delete_from_blacklist(id){
    $('#blacklist_body').find('#'+id).remove()
}
function delete_from_suggestions(id){
    $('#suggestions_body').find('#'+id).remove()
}
function delete_from_searchterms(id){
    var term = $('#searchterms_body').find('#'+id)
    term.remove()
}
function add_to_whitelist(SmObjId, PiqYear, PiqSession, held_in, title){
    var url = baseUrlVvzUzh+PiqYear+'/'+PiqSession+'/SM/'+SmObjId
    var module = $(`<tr data-semester="${PiqYear} ${PiqSession}" id="${SmObjId}" class="shown"><td><a target="_blank" href="${url}">${title}</a></td><td>${convert_session_to_string(held_in, PiqYear)}</td><td><button name="Verbergen" onclick="whitelist_from_blacklist('${SmObjId}', '${PiqYear}', '${PiqSession}', '${held_in}', '${title}')">Verbergen</button></td></tr>`)
    $('#whitelist_body').append(module)
}
function add_to_blacklist(SmObjId, PiqYear, PiqSession, held_in, title){
    var url = baseUrlVvzUzh+`${PiqYear}/${PiqSession}/SM/${SmObjId}`
    var module = $(`<tr data-semester="${PiqYear} ${PiqSession}" id="${SmObjId}" class="shown"><td><a target="_blank" href="${url}">${title}</a></td><td>${convert_session_to_string(held_in, PiqYear)}</td><td><button name="Anzeigen" onclick="whitelist_from_blacklist('${SmObjId}', '${PiqYear}', '${PiqSession}', '${held_in}', '${title}')">Anzeigen</button></td></tr>`)
    $('#blacklist_body').append(module)
}
function add_to_suggestions(SmObjId, PiqYear, PiqSession, held_in, title){
    var url = baseUrlVvzUzh+PiqYear+'/'+PiqSession+'/SM/'+SmObjId
    var module = $(`<tr data-semester="${PiqYear} ${PiqSession}" id="${SmObjId}" class="shown"><td><a target="_blank" href="${url}">${title}</a></td><td>${convert_session_to_string(held_in, PiqYear)}</td><td><button name="Anzeigen" onclick="whitelist_from_blacklist('${SmObjId}', '${PiqYear}', '${PiqSession}', '${held_in}', '${title}')">Anzeigen</button><button name="Verbergen" onclick="whitelist_from_blacklist('${SmObjId}', '${PiqYear}', '${PiqSession}', '${held_in}', '${title}')">Verbergen</button></td></tr>`)
    $('#suggestions_body').append(module)
}
function add_to_searchterms(id, term){
    var searchterm = $('<tr id="'+id+'"><td>'+term+'</td><td><button onclick="remove_searchterm('+id+')">Entfernen</button></td></tr>')
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
                add_to_whitelist(data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].held_in, data[row].title)
            }
            whitelist.prepend('<tr><td><input type="text" id="whitelist_text" spellcheck="false" placeholder="Modulnummer (8-Stellige Zahl in der URL zum Modul)" style="width: 90%"></td><td colspan="2"><button name="submit_whitelist" style="display: block; width: 100%" type="button" onclick="save_module()">Modul hinzufügen</button></td></tr>')

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
                add_to_blacklist(data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].held_in, data[row].title)
            }
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
                add_to_suggestions(data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].PiqSession, data[row].title)
            }
        },
        error : function (err) {
            console.log('Suchvorschläge konnten nicht abgerufen werden: '+err)
        }

    })
}

function convert_session_to_string(session, year){
    if (session == 3){
        return `HS ${year % 100 || ''}`
    }
    if (session == 4){
        return `FS ${year % 100 || ''}`
    }
    if (session == 999){
        return `HS & FS ${year % 100 || ''}`
    }
    else{
        return 'undefiniert'
    }

}

$(document).ready(function () {
    $('#anchor-admin-2').accordion({collapsible:true,heightStyle:'content'})
});