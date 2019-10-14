// GLOBAL VARIABLES DEFINITIONS: used across public.js and filter.js
baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
apiUrl = 'https://greenvvz.ifi.uzh.ch'
// apiUrl = 'http://127.0.0.1:8080/'
secret_key = $('#anchor-admin').data('api-key') || $('#anchor-admin-2').data('api-key')
// initializatin of global vars for sp_idlist and sp_textlist
studyprogram_idlist = []
studyprogram_textlist = []

/**
 * Flag tablerows for modules OF THE WHITELIST ONLY contained in the studyprogram input 
 * via #studyprogram_input.
 * @param {Number} [module_id]  numerical part of the module CSS selector id.
 * @param {Number} SmObjId      course catalogue id.
 * @param {Number} PiqYear      course catalogue year.
 * @param {Number} PiqSession   course catalogue year.
 * @param {Boolean} whitelisted  whitelist status of the module to save.
 * @param {String} searchterm   searchterm which found the module in the course catalogue
 */
async function post_module_to_db(module_id, SmObjId, PiqYear, PiqSession, whitelisted, searchterm, searchterm_id) {
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
            'searchterm_id': searchterm_id,
        }),
        success : function (data) {
            // if module_id not supplied, it was added using save_module()
            if(module_id) flag_in_suggestions(module_id, whitelisted);
            populate_whitelist();
            populate_blacklist();
            populate_studyprograms();
        },
        error : function (err) {
            alert(`Das Modul konnte nicht als ${whitelisted ? 'whitelisted' : 'blacklisted'} gespeichert werden`)
        }
    })
}

/**
 * Flag tablerows for modules OF THE WHITELIST ONLY contained in the studyprogram input 
 * via #studyprogram_input.
 * @param {Number} module_id    numerical part of the module CSS selector id, matches the DB id for saved modules.
 * @param {Boolean} whitelisted  whitelist status of the module to save.
 */
async function update_whitelist_status(module_id, whitelisted) {
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

/**
 * Save searchterm from input into the DB.
 */
async function save_searchterm(){
    var term = $('#searchterm_text').val().trim()
    if(term == '') {
        alert('Eingabe fehlt');
        return;
    }
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
/**
 * Update searchterm from input to the DB.
 */
async function update_searchterm(id){
    var term = $('#searchterms_body').find(`#${id} td.searchterm`).text()
    if(term == '') {
        delete_searchterm(id);
        return;
    }
    await $.ajax({
        url :  `${apiUrl}/searchterms/${id}?key=${secret_key}`,
        method : 'PUT',
        dataType : 'json',
        data : {'term':term},
        success : function (data) {
            populate_searchterms()
            populate_suggestions()
        },
        error : function (err) {
            alert('Der Suchbegriff konnte nicht gespeichert werden')
        }

    })
}

/**
 * Delete searchterm from the DB.
 * @param {Number} id DB id for searchterm to delete
 */
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
/**
 * Remove searchterm from the DOM.
 * @param {Number} id numerical part of CSS selector id for searchterm to delete, matches DB id.
 */
function remove_from_searchterms(id){
    var term = $('#searchterms_body').find('#'+id)
    term.remove()
}

/**
 * Save module from SmObjId input into the DB, using the selected semester or current if all selected.
 */
async function save_module(){
    // get SmObjId input
    var SmObjId = $('#whitelist_text').val()
    // If all semesters selected, select current one, then go ahead.
    if($('option:selected').val() == 'all_years all_semesters') {
        alert('Alle Semester ausgewählt. Das modul wird im jetzigen Semester gespeichert.')
        $(`option[value="${$('.current_semester').val()}"]`).prop('selected', true);
    }
    // get year and semester data
    var PiqYear = $('option:selected').val().split(' ')[0];
    var PiqSession = $('option:selected').val().split(' ')[1];
    // post to db with module_id=null, and searchterm = "Manuell Hinzugefügt"
    await post_module_to_db(null, SmObjId, PiqYear, PiqSession, whitelisted=1, "Manuell Hinzugefügt", -999);
}
/**
 * Delete module from the DB.
 * @param {Number} module_id DB id for module to delete
 */
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

/**
 * Remove module from the DOM.
 * @param {Number} module_id the numerical part of the CSS selector, matches DB id.
 */
function remove_module(module_id){
    document.getElementById(`module_${module_id}`).remove()
}

/**
 * Flag module as whitelisted or blacklisted in the suggestions, changing Status and (de)activates corresponding buttons.
 * @param {Number} module_id the numerical part of the CSS selector
 * @param {Boolean} whitelisted the whitelist status
 */
function flag_in_suggestions(module_id, whitelisted){
    var tr_module = document.getElementById(`module_${module_id}`);

    if(whitelisted==1) {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = true;
        tr_module.querySelector('button[name="Verbergen"]').disabled = false;
        tr_module.children[4].innerHTML = "Angezeigt"; // status
    }
    else if(whitelisted==0) {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = false;
        tr_module.querySelector('button[name="Verbergen"]').disabled = true;
        tr_module.children[4].innerHTML = "Verborgen"; // status
    }
    else {
        tr_module.querySelector('button[name="Anzeigen"]').disabled = false;
        tr_module.querySelector('button[name="Verbergen"]').disabled = false;
        tr_module.children[4].innerHTML = "Neu"; // status
    }
}

/**
 * Generate generalizable part of table row for a given module - what differs are buttons and suffixes.
 * @param {Number} [module_id]  numerical part of the module CSS selector id, mismatches DB id if in suggestions
 * @param {Number} SmObjId      course catalogue id
 * @param {Number} PiqYear      course catalogue year
 * @param {Number} PiqSession   course catalogue year
 * @param {String} title        module title
 * @param {String} searchterm   searchterm which found the module in the course catalogue
 * @return {String} String matching an opened tr DOM element, with td elements inside
 */
function write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    // courses.uzh.ch url
    var url = baseUrlVvzUzh+PiqYear+'/'+PiqSession+'/SM/'+SmObjId;
    // write id for tr, as well as data-SmObjId and data-semester, descriptive class="shown" by default.
    if(searchterm.charAt(0)=='#') {
        var searchterm_td = `<td class="searchterm deleted">${searchterm/*.slice(2)*/}</td>`
    }
    else {
        var searchterm_td = `<td class="searchterm">${searchterm}</td>`
    }
    return `<tr id="module_${module_id}" data-SmObjId="${SmObjId}" data-semester="${PiqYear} ${PiqSession}" class="shown">
        <td><a target="_blank" href="${url}">${title}</a></td>
        ${searchterm_td}
        <td>${convert_session_to_string(PiqSession, PiqYear)}</td>
        `
}

/**
 * Write table row for module in whitelist, append to whitelist table
 * @param {Number} [module_id]  numerical part of the module CSS selector id, matches DB id
 * @param {Number} SmObjId      course catalogue id
 * @param {Number} PiqYear      course catalogue year
 * @param {Number} PiqSession   course catalogue year
 * @param {String} title        module title
 * @param {String} searchterm   searchterm which found the module in the course catalogue
 */
function add_to_whitelist(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
        <td><button name="Anzeigen" onclick="update_whitelist_status(${module_id}, 0)">Verbergen</button></td>
    </tr>`)
    $('#whitelist_body').append(module);
}

/**
 * Write table row for module in blacklist, append to blacklist table
 * @param {Number} [module_id]  numerical part of the module CSS selector id, matches DB id
 * @param {Number} SmObjId      course catalogue id
 * @param {Number} PiqYear      course catalogue year
 * @param {Number} PiqSession   course catalogue year
 * @param {String} title        module title
 * @param {String} searchterm   searchterm which found the module in the course catalogue
 */
function add_to_blacklist(module_id, SmObjId, PiqYear, PiqSession, title, searchterm){
    var anzeigen_button = `<button name="Anzeigen" onclick="update_whitelist_status(${module_id}, 1)">Anzeigen</button>`
    var   delete_button = `<button name="Löschen" onclick="delete_blacklisted_module(${module_id})">Löschen</button>`
    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
            <td>${anzeigen_button}${delete_button}</td>
        </tr>`)
    $('#blacklist_body').append(module);
}

/**
 * Write table row for module in suggestions, append to suggestions table
 * @param {Number} [module_id]  numerical part of the module CSS selector id, matches DB id
 * @param {Number} SmObjId      course catalogue id
 * @param {Number} PiqYear      course catalogue year
 * @param {Number} PiqSession   course catalogue year
 * @param {String} title        module title
 * @param {Boolean} whitelisted whitelisted the whitelist status
 * @param {String} searchterm   searchterm which found the module in the course catalogue
 * @param {Number} searchterm_id searchterm which found the module in the course catalogue
 */
function add_to_suggestions(module_id, SmObjId, PiqYear, PiqSession, title, whitelisted, searchterm, searchterm_id){
    // write both anzeigen and verbergen button, disabled depending on if module is white- or blacklisted or neither.
    var anzeigen_button=`<button name="Anzeigen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=1, '${searchterm}', ${searchterm_id})"
        ${whitelisted==1 ? 'disabled' : ''}>Anzeigen</button>`
    var verbergen_button=`<button name="Verbergen" onclick="post_module_to_db(${module_id}, ${SmObjId}, ${PiqYear}, ${PiqSession}, whitelisted=0, '${searchterm}', ${searchterm_id})"
        ${whitelisted==0 ? 'disabled' : ''}>Verbergen</button>`
    if(whitelisted==1) {
        sug_status='Angezeigt';
    }
    else if(whitelisted==0) {
        sug_status='Verborgen';
    }
    else {
        sug_status='Neu';
    }
    var whitelist_status_td = `<td class="whitelist_status whitelisted_${whitelisted}">${sug_status}</td>`

    var module = $(`${write_tr_prefix_for_list(module_id, SmObjId, PiqYear, PiqSession, title, searchterm)}
            <td>${anzeigen_button}${verbergen_button}</td>
            ${whitelist_status_td}
        </tr>`);
    $('#suggestions_body').append(module)
}

/**
 * Write table row for searchterm and add to DOM.
 * @param {Number} id           numerical part of the searchterm CSS selector id, matches DB id
 * @param {String} term         searchterm value
 */
function add_to_searchterms(id, term){
    if(term.charAt(0) != '#') {
        var searchterm = $('<tr id="'+id+'"><td class="searchterm">'+term+'</td><td><button class="searchterm_mod" onclick="delete_searchterm('+id+')">Entfernen</button></td></tr>')
        $('#searchterms_body').append(searchterm)
    }

}



/**
 * Request searchterms from server, add them to DOM.
 */
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
            // if they should be disabled, do it again
            if($('.searchterm_mod').prop('disabled')) {
                $('.searchterm_mod').prop('disabled', true);
            }
        }
    })


}

/**
 * Request whitelisted modules from server, add them to DOM.
 */
async function populate_whitelist(){
    var whitelist = $('#whitelist_body')
    await $.ajax({
        url: apiUrl+'/modules/whitelist',
        method : 'GET',
        beforeSend: function () { 
            // show loading indicators
            $('#whitelist').find('div.loading-overlay').toggle(); 
            $('#count_whitelist').addClass('loading-count').html('<span>.</span><span>.</span><span>.</span>');
        },
        success : function (data) {
            // remove all tr from body
            whitelist.empty()
            for (var row in data) {
                // for each module in data, add a row
                add_to_whitelist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].searchterm)
            }
            // hide modules not in current filter scope
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Whitelist konnte nicht abgerufen werden: '+err)
        },
        complete : function() {
            // hide loading screen
            $('#whitelist').find('div.loading-overlay').toggle();
            // update number badge
            $('#count_whitelist').removeClass('loading-count').html($('#whitelist_body').find($(`.shown`)).length)
            // update filter entries & resort for tablesorter
            retrigger_table_filter('whitelist');
        }

    })

}

/**
 * Request blacklisted modules from server, add them to DOM.
 */
async function populate_blacklist(){
    var blacklist = $('#blacklist_body');
    await $.ajax({
        url: apiUrl+'/modules/blacklist',
        method : 'GET',             // show loading screen
        beforeSend: function () {
            $('#blacklist').find('div.loading-overlay').toggle(); 
            $('#count_blacklist').addClass('loading-count').html('<span>.</span><span>.</span><span>.</span>');
        },
        success : function (data) {
            // remove all tr from body
            blacklist.empty()
            for (var row in data) {
                // for each module in data, add a row
                add_to_blacklist(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].searchterm)
            }
            // hide modules not in current filter scope
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Blacklist konnte nicht abgerufen werden: '+err)
        },
        complete : function() {
            // hide loading screen
            $('#blacklist').find('div.loading-overlay').toggle();
            // update the number badge
            $('#count_blacklist').removeClass('loading-count').html($('#blacklist_body').find($(`.shown`)).length)
            // update filter entries & resort for tablesorte
            retrigger_table_filter('blacklist');    
        }
    })
}

/**
 * Request found modules from server, add them to DOM.
 */
async function populate_suggestions(){
    var suggestions = $('#suggestions_body')
    await $.ajax({
        url: apiUrl+'/search',
        method : 'GET',
        beforeSend: function () {
            $('#suggestions').find('div.loading-overlay').toggle();
            $('#count_suggestions').addClass('loading-count').html('<span>.</span><span>.</span><span>.</span>');
            // disable editing searchterms, would retrigger search
            $('.searchterm_mod').prop('disabled', true);

        },
        success : function (data) {
            // remove all tr from body
            suggestions.empty()
            for (var row in data) {
                // for each module in data, add a row
                add_to_suggestions(data[row].id, data[row].SmObjId, data[row].PiqYear, data[row].PiqSession, data[row].title, data[row].whitelisted, data[row].searchterm, data[row].searchterm_id)
            }
            // hide modules not in current filter scope
            ShowSelectedModules();
        },
        error : function (err) {
            console.log('Suchvorschläge konnten nicht abgerufen werden: '+err)
        },
        complete : function() {
            // hide loading screen
            $('#suggestions').find('div.loading-overlay').toggle();
            // update the number badge
            $('#count_suggestions').removeClass('loading-count').html($('#suggestions_body').find($(`.shown`)).length);
            // enable save search term button
            $('.searchterm_mod').prop('disabled', false);
            // update filter entries & resort for tablesorter
            retrigger_table_filter('suggestions');         
        }

    })
}

function retrigger_table_filter(tableName) {
    // tell tablesorter to resort
    $(`${tableName} table`).trigger('update');
    // hack: put something into name des moduls filter, let it load, clear, to retrigger other filters
    var sug_filter_input = $(`#${tableName}>table thead td[data-column="0"]:not(#${tableName}_title_th) input`).val('...').blur();
    setTimeout(function(){
        $(`#${tableName}>table thead td[data-column="0"]:not(#${tableName}_title_th) input`).val('').blur()
    }, 300);
}

/**
 * Request studyprograms for selected semester from server, as well as studyprogamid_moduleids list, add them to global JS scope.
 */
async function populate_studyprograms() {
    // get selected semester
    var PiqYear = $('option:selected').val().split(' ')[0];
    var PiqSession = $('option:selected').val().split(' ')[1];
    var previous_placeholder = $('#studyprogram_input').attr("placeholder")
    // get studyprograms id list and text list 
    await $.ajax({
        url: apiUrl+'/studyprograms',
        method : 'GET',
        data: {
            'PiqYear': PiqYear,
            'PiqSession': PiqSession,
        },
        beforeSend: function () { 
            // loading designator, disable button
            $('#studyprogram_input').attr("placeholder", "Lade Studienprogramme...").prop('disabled', true); },
        success : function (data) {
            // data is two lists, one for ids, one for texts, with matching indexing.
            studyprogram_idlist = data[0]
            studyprogram_textlist = data[1]
        },
        error : function (err) {
            console.log('/studyprograms konnten nicht abgerufen werden: '+err)
        },
        complete : function() {
            // overwrite loading designator, enable button
            $('#studyprogram_input').attr("placeholder", previous_placeholder).prop('disabled', false);
        },
    })

    // get studyprogram_id : [module_ids] dictionary
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
    $('#studyprogram_input').autocomplete({
        // HACK custom filter function for no or too many results
        source: function(request, response) {
            var results = $.ui.autocomplete.filter(studyprogram_textlist, request.term);
            var num_sp_suggestions = 10;
            /* Use this to limit total results instead of scrollbar */
            // if (results.length > num_sp_suggestions+5) {
            //     // will be rendered differently, see filter.js
            //     var total_msg=` ... ${results.length - num_sp_suggestions}`
            //     results = results.slice(0, 10)
            //     results.push(total_msg)
            // }
            if (results.length == 0) {
                results.push(' Keine ')
            }
            response(results);
        },
        minLength: 0,
        delay: 0,
    }).focus(function() {
        // show all entries on focus
        $(this).autocomplete('search', $(this).val());
    });
    // for iFrameResizer
    $('.ui-autocomplete').attr('data-iframe-height', '');
}

/**
 * Convert session to human readable span element as string.
 * @param  {Number} session session code, either 3, 4, 003, 004.
 * @param  {Number} year    module year data.
 * @return {String} A span containing the humanreadable semester and year.
 */
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

/**
 * Execute update function in backend, update names or remove modules which no longer exist in their semester.
 */
async function updateModules() {
    await $.ajax({
        url: apiUrl+'/update',
        method : 'GET',
        beforeSend: function () {
            // generate and add alert box to DOM
            $('#anchor-admin').before(`
            <div id="modules-updating" class="alert alert-blue">
            <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                <h3>Module werden aktualisiert</h3><p>Bitte haben Sie Geduld, dies kann je nach Anzahl der Module bis zu einer Minute dauern</p>
            </div>
            `)
        },
        error : function (err) {
            console.log(err)
            // make alert box red and error
            $('#modules-updating').removeClass('alert-blue').addClass('alert-red')
            $('#modules-updating').find($('h3')).text('Die Module konnten nicht aktualisiert werden.')
            $('#modules-updating').find($('p')).text('Bitte versuchen Sie es erneut, in dem Sie die Seite neu laden.')
        },
        success : function() {
            populate_whitelist();
            populate_blacklist();
            // hide alert box, set cookie for an hour
            $('#modules-updating').hide();
            setCookie("updated_recently", true, 1);
        },
    })
}

/**
 * Save a cookie which expires after exdays days.
 * @param {String} cname    name of the cookie
 * @param          cvalue   value of the cookie
 * @param {Number} exdays   days until cookie expires
 */
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
/**
 * Get cookie by name
 * @param {String} cname    name of the cookie
 * @return {String}         the value of the cookie
 */
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
/**
 * Check if the "updated_recently" cookie exists - if it doesn't, updateModules()
 */
function checkUpdatedCookie() {
    var update_status = getCookie("updated_recently");
    if (update_status != "") {
        return;
    } else {
        updateModules();
    }
}

/* ######################## JQUERY EVENT HANDLERS ########################### */

/**
 * Edit the searchterm text on click (is in first td per row)
 */
$(document).on( "click", "#searchterms_body td.searchterm", function() {
    if($('.searchterm_mod').prop('disabled') == false) {
        $(this).attr("contentEditable", true);
        $(this).attr("data-initial", $(this).text());
    }
});
$(document).on( "blur", "#searchterms_body td.searchterm", function() {
    $(this).attr("contentEditable", false);
        if($(this).text() != $(this).attr("data-initial")) {
            update_searchterm($(this).parent().attr('id'));
        }
});