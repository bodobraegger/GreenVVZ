$(document).ready(function () {
    $('#anchor-admin-2').accordion({collapsible:true,heightStyle:'content'})
    // update modules
    $.ajax({
        url: apiUrl+'update',
        method : 'GET',
        beforeSend: function () {
            $(":input").prop("disabled", true);
            $('#anchor-admin').before('<div id="loading"><h2>Module werden aktualisiert</h2><p>Bitte haben Sie Geduld, dies kann je nach Anzahl der Module bis zu einer Minute dauern</p></div>')
        },
        success : function (data) {
            var root = $('#anchor-admin')
            // prepare lists
            var whitelist =     $('<h3>Angezeigte Elemente (Whitelist)</h3><div style="padding: 0"><table><thead><td>Name der Lehrveranstaltung</td><td>Semster</td><td>Verbergen</td></thead><tbody id="whitelist_body"></tbody></table></div>')
            var searchterms =   $('<h3>Suchbegriffe</h3><div style="padding: 0"><table><thead><td>Begriff</td><td>Entfernen</td></thead><tbody id="searchterms_body"></tbody></table></div>')
            var suggestions =   $('<h3>Vorschläge basierend auf Suchbegriffen</h3><div style="padding: 0"><table><thead><td>Name der Lehrveranstaltung</td><td>Semster</td><td>Anzeigen/Verbergen</td></thead><tbody id="suggestions_body"></tbody></table></div>')
            var blacklist =     $('<h3>Verborgene Elemente (Blacklist)</h3><div style="padding: 0"><table><thead><td>Name der Lehrveranstaltung</td><td>Semster</td><td>Anzeigen</td></thead><tbody id="blacklist_body"></tbody></table></div>')
            root.append(whitelist,searchterms,suggestions,blacklist)
            // populate searchterms
            populate_searchterms()

            // populate whitelist
            populate_whitelist()

            // populate blacklist
            populate_blacklist()

            // populate suggestions
            populate_suggestions()

            // make accordion
            $('#anchor-admin').accordion({collapsible:true,heightStyle:'content'})
        },
        error : function (err) {
            alert('Die Module konnten nicht aktualisiert werden')
        },
        complete: function () {
            $(":input").prop("disabled", false);
            $('#loading').hide()
        }

    })

    
});