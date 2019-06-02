/**
 * Flag tablerows for modules in the semester chosen by the dropdown selector "semester".
 * @return {jQuery()} The tablerows of modules matching the currently selected semester.
 */
function FlagSelectedSemester() {
    var year_semester = $("option:selected").val();
    // if all semesters are selected, look for year_semester tags containing a space (all do)
    if($("option:selected").val() == 'all_years all_semesters') year_semester=" ";
    $('[data-semester]').removeClass('selected-semester');
    $(`[data-semester*="${year_semester}"]`).addClass('selected-semester');
    return $('.selected-semester');
}

/**
 * Flag tablerows for modules OF THE WHITELIST ONLY contained in the studyprogram input 
 * via #studyprogram_input.
 * @return {jQuery()} The tablerows of modules in the whitelist matching the currently selected studyprogram.
 */
function FlagSelectedStudyprogram() {
    // since /studyprograms delivers two lists, sp_idlist and sp_textlist, the autocomplete
    // suggests an entry of the textlist. the index matches across them, so you can get the id.
    var studyprogram_index = studyprogram_textlist.indexOf(document.getElementById("studyprogram_input").value);
    // no entry in sp_textlist found, return all modules
    if(studyprogram_index == -1) {
        // make clear filter button inactive
        $('#studyprogram_btn_clear').prop('disabled', true);
        // if no input was given, do nothing, else log invalid input
        document.getElementById("studyprogram_input").value ? console.log("invalid input: " + document.getElementById("studyprogram_input").value) : "";
        // mark all module row in the whitelist as selected
        $('#whitelist_body').find($(`[data-semester]`)).addClass('selected-studyprogram');
    }
    // else find the id of the studyprogram using the index, and find corresponding the module_ids 
    else {
        studyprogram_id = studyprogram_idlist[studyprogram_index];
        var module_ids = studyprogramid_moduleids[studyprogram_id];
        var modules_to_unflag = $('#whitelist_body').find($(`[data-semester]`));
        // mark modules not in modules as not selected, select the ones in module_ids
        for(i = 0; i < module_ids.length; i++) {
            modules_to_unflag = modules_to_unflag.not($(`#module_${module_ids[i]}`));
            $(`#module_${module_ids[i]}`).addClass('selected-studyprogram');
        }
        $(modules_to_unflag).removeClass('selected-studyprogram');
        // make the clear filter button active 
        $('#studyprogram_btn_clear').prop('disabled', false);
    }
    return $('.selected-studyprogram');
}

/**
 * Render items using CSS classes according to their selection status
 * @return {jQuery()} The tablerows of modules matching the current filters.
 */
function ShowSelectedModules() {
    // find modules for semester according to dropdown
    FlagSelectedSemester();
    // find modules in whitelist for studyprogram according to input
    FlagSelectedStudyprogram();

    // hide all modules, then unhide modules for the selected semester(s)
    $('[data-semester]').addClass('hidden').removeClass('shown');
    $('[data-semester].selected-semester').removeClass('hidden').addClass('shown');
    // hide all whitelist elements, unhide modules for selected studyprogram
    $('#whitelist_body').find($('[data-semester]')).addClass('hidden').removeClass('shown');
    $('#whitelist_body').find($(`[data-semester].selected-semester.selected-studyprogram`)).removeClass('hidden').addClass('shown');
    
    // update the number badges for each table
    $('#count_whitelist').html($('#whitelist_body').find($(`.shown`)).length)
    $('#count_suggestions').html($('#suggestions_body').find($(`.shown`)).length)
    $('#count_blacklist').html($('#blacklist_body').find($(`.shown`)).length)
    return $('.shown');
}
/**
 * Clear the studyprogram input
 */
function ClearStudyProgramFilter() {
    document.getElementById("studyprogram_input").value = "";
    ShowSelectedModules();
}

/**
 * monkey patch into jquery autocomplete, for custom rendering and highlighting found elements,
 * and if necessary, searching only from beginning of result (commented out)
 */
function monkeyPatchAutocomplete() {
    // hack: override autocomplete _renderItem to highlight matching part
    $.ui.autocomplete.prototype._renderItem = function (ul, item) {
        // Escape any regex syntax inside this.term
        var cleanTerm = this.term.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        
        // Build pipe separated string of terms to highlight
        var keywords = $.trim(cleanTerm).replace('  ', ' ').split(' ').join('|');
        
        var re = new RegExp("(" + keywords + ")", "gi");
        // further hack: displaying custom total message, see admin.js
        // if more than num_sp_sugs+5 suggestions, show only 10 
        if(item.label.includes(' ... ')) {
            var listend = $("<li>")
            if(keywords.length > 0) {
                listend.html(`<b>${item.label}</b> weitere Studienprogramme für Module im gewählten Semester mit Filter: <b>${$.trim(cleanTerm).replace('  ', ' ')}</b>`);
            }
            else {
                listend.html(`<b>${item.label}</b> weitere Studienprogramme für Module im gewählten Semester`);
            }
            return listend.attr('id', 'further_studyprograms_msg').appendTo(ul);
        }
        // if no suggestions pop up, show 'Keine' message
        else if(item.label.includes(' Keine ')) {
            return $("<li>").html(`<b>${item.label}</b> Studienprogramme für Module im gewählten Semester mit Filter: <b>${$.trim(cleanTerm).replace('  ', ' ')}</b>`).attr('id', 'further_studyprograms_msg').appendTo(ul);
        }
        // Get the new label text to use with matched terms wrapped
        // in a span tag with a class to do the highlighting
        var output = item.label.replace(re,  
            '<span class="ui-menu-item-highlight">$1</span>');
        return $("<li>")
            .append($("<a>").html(output))
            .appendTo(ul);
    };
    // hack: override autocomplete search function compare starts of options ("^")
    /* $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
            return matcher.test(value.label || value.value || value);
        });
    }; */
};
// apply the patch on script load
$(function () {
    monkeyPatchAutocomplete();
});
