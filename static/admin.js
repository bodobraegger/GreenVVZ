var baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
var apiUrl = 'https://greenvvz.ifi.uzh.ch'
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
    if($('option:selected') == 'all_years all_semesters') {
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[0]
        var PiqSession = $('#filter_selectors').find('optgroup').find('option').val().split(' ')[1]
    }
    else {
        var PiqYear = $('option:selected').val().split(' ')[0];
        var PiqSession = $('option:selected').val().split(' ')[1];
    }
    await $.ajax({
        url: `${apiUrl}/modules/?key=${secret_key}`,
        data: JSON.stringify({
            'PiqYear': PiqYear,
            'PiqSession': PiqSession,
            'SmObjId': SmObjId,
            'whitelisted': 1,
        }),
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
    var tr_module = document.getElementById(`module_${module_id}`);

    if(whitelisted==1) {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = true;
        tr_module.querySelector('button[name="Verbergen"]').disabled = false;
        tr_module.children[4].innerHTML = "Angezeigt";
    }
    else if(whitelisted==0) {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = false;
        tr_module.querySelector('button[name="Verbergen"]').disabled = true;
        tr_module.children[4].innerHTML = "Verborgen";
    }
    else {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = false;
        tr_module.querySelector('button[name="Verbergen"]').disabled = false;
        tr_module.children[4].innerHTML = "Neu";
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
    $('#whitelist_body').append(module);
}
function add_to_blacklist(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var anzeigen_button = `<button name="Anzeigen" onclick="update_whitelist_status(${module_id}, 1)">Anzeigen</button>`
    var   delete_button = `<button name="Löschen" onclick="delete_blacklisted_module(${module_id})">Löschen</button>`
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
            <td>${anzeigen_button}${delete_button}</td>
        </tr>`)
    $('#blacklist_body').append(module);
}
function add_to_suggestions(module_id, SmObjId, PiqYear, PiqSession, title, whitelisted, searchterm){
    var anzeigen_button=`<button name="Anzeigen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=1, '${searchterm}')"
        ${whitelisted==1 ? 'disabled' : ''}>Anzeigen</button>`
    var verbergen_button=`<button name="Verbergen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=0, '${searchterm}')"
        ${whitelisted==0 ? 'disabled' : ''}>Verbergen</button>`
    if(whitelisted==1) {
        sug_status='Angezeigt';
        sort_key=2;
    }
    else if(whitelisted==0) {
        sug_status='Verborgen';
        sort_key=3
    }
    else {
        sug_status='Neu';
        sort_key=1
    }
    var whitelist_status_td = `<td class="whitelist_status whitelisted_${whitelisted}" sorttable_customkey="${sort_key}">${sug_status}</td>`

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
            whitelist.prepend(`
            <tr class="static" data-row-index="0">
              <td colspan="2">
                <input type="text" id="whitelist_text" spellcheck="false" placeholder="Modulnummer (8-Stellige Zahl in der URL zum Modul)" style="width: 90%">
              </td>
              <td colspan="2">
                <button name="submit_whitelist" style="display: block; width: 100%" type="button" onclick="save_module()">Modul hinzufügen</button>
              </td>
            </tr>`)
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Whitelist konnte nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#whitelist table').trigger('update');
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
            $('#blacklist table').trigger('update');
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
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Suchvorschläge konnten nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#suggestions table').trigger('update');
            $('#suggestions').find('div.loading').toggle();
        }

    })
}

async function populate_studyprograms() {
    var PiqYear = $('option:selected').val().split(' ')[0];
    var PiqSession = $('option:selected').val().split(' ')[1];
    await $.ajax({
        url: apiUrl+'/studyprograms',
        method : 'GET',
        data: {
            'PiqYear': PiqYear,
            'PiqSession': PiqSession,
        },
        beforeSend: function () { $('#studyprogram_input').attr("placeholder", "Lade Studienprogramme...").prop('disabled', true); },
        success : function (data) {
            studyprogram_idlist = data[0]
            studyprogram_textlist = data[1]
        },
        error : function (err) {
            console.log('/studyprograms konnten nicht abgerufen werden: '+err)
        },
        complete : function() {
            $('#studyprogram_input').attr("placeholder", "Studienprogramm").prop('disabled', false);
        },
    })
    await $.ajax({
        url: apiUrl+'/studyprograms_modules',
        method : 'GET',
        success : function (data) {
            studyprogramid_moduleids = data;
        },
        error : function (err) {
            console.log('/studyprograms_modules konnte nicht abgerufen werden: '+err)
        },
    })
    // update the autocomplete list
    // autocomplete(document.getElementById("studyprogram_input"), studyprogram_textlist);
    $('#studyprogram_input').autocomplete({
        source: function(request, response) {
            var results = $.ui.autocomplete.filter(studyprogram_textlist, request.term);
            var num_sp_suggestions = 10;
            if (results.length > num_sp_suggestions+5) {
                // will be rendered differently, see filter.js
                var total_msg=` ... ${results.length - num_sp_suggestions}`
                results = results.slice(0, 10)
                results.push(total_msg)
            }
            if (results.length == 0) {
                results.push(' Keine ')
            }
            response(results);
        },
        minLength: 0,
        delay: 0,
    }).focus(function() {
        $(this).autocomplete('search', $(this).val());
    });
    $('.ui-autocomplete').attr('data-iframe-height', '');
}

function convert_session_to_string(session, year){
    if (session == 3){
        return `<span style="display: none;">${year % 100 || ''}</span><span class="semester">HS </span>${year % 100 || ''}`
    }
    if (session == 4){
        return `<span style="display: none;">${(year+1) % 100 || ''}</span><span class="semester">FS </span>${(year+1) % 100 || ''}`
    }
    else{
        return 'undefiniert'
    }
}

function updateModules() {
    // update modules
    $.ajax({
        url: apiUrl+'/update',
        method : 'GET',
        beforeSend: function () {
            $('#anchor-admin').before(`
            <div id="modules-updating" class="alert alert-blue">
            <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                <h3>Module werden aktualisiert</h3><p>Bitte haben Sie Geduld, dies kann je nach Anzahl der Module bis zu einer Minute dauern</p>
            </div>
            `)
        },
        error : function (err) {
            console.log(err)
            $('#modules-updating').removeClass('alert-blue').addClass('alert-red')
            $('#modules-updating').find($('h3')).text('Die Module konnten nicht aktualisiert werden.')
            $('#modules-updating').find($('p')).text('Bitte versuchen Sie es erneut, in dem Sie die Seite neu laden.')
        },
        success : function() {
            // populate whitelist
            populate_whitelist();
            // populate blacklist
            populate_blacklist();
            $('#modules-updating').hide();
            setCookie("updated_recently", true, 1);
        },
    })
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkUpdatedCookie() {
    var update_status = getCookie("updated_recently");
    if (update_status != "") {
        return;
    } else {
        updateModules();
    }
}
