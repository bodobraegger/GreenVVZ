function FlagSelectedSemester() {
    var year_semester = $("option:selected").val();
    // if all semesters are selected, look for year_semester tags containing a space (all do)
    if($("option:selected").val() == 'all_years all_semesters') year_semester=" ";
    $('[data-semester]').removeClass('selected-semester');
    $(`[data-semester*="${year_semester}"]`).addClass('selected-semester');
    return;
}
function FlagSelectedStudyprogram() {
    var studyprogram_index = studyprogram_textlist.indexOf(document.getElementById("studyprogram_input").value);
    if(studyprogram_index == -1) {
        $('#studyprogram_btn_clear').prop('disabled', true);
        document.getElementById("studyprogram_input").value ? console.log("invalid input: " + document.getElementById("studyprogram_input").value) : "";
        $('#whitelist_body').find($(`[data-semester]`)).addClass('selected-studyprogram');
        return;
    }
    studyprogram_id = studyprogram_idlist[studyprogram_index];
    var module_ids = studyprogramid_moduleids[studyprogram_id];
    var modules_to_unflag = $('#whitelist_body').find($(`[data-semester]`));
    
    for(i = 0; i < module_ids.length; i++) {
        modules_to_unflag = modules_to_unflag.not($(`#module_${module_ids[i]}`));
        $(`#module_${module_ids[i]}`).addClass('selected-studyprogram');
    }
    $(modules_to_unflag).removeClass('selected-studyprogram');
    $('#studyprogram_btn_clear').prop('disabled', false);
    return;
}
function ShowSelectedModules() {
    FlagSelectedSemester();
    FlagSelectedStudyprogram();
    $('[data-semester]').addClass('hidden').removeClass('shown');
    $('[data-semester].selected-semester').removeClass('hidden').addClass('shown');
    
    $('#whitelist_body').find($('[data-semester]')).addClass('hidden').removeClass('shown');
    $('#whitelist_body').find($(`[data-semester].selected-semester.selected-studyprogram`)).removeClass('hidden').addClass('shown');
    
    $('#count_whitelist').html($('#whitelist_body').find($(`.shown`)).length)
    $('#count_suggestions').html($('#suggestions_body').find($(`.shown`)).length)
    $('#count_blacklist').html($('#blacklist_body').find($(`.shown`)).length)
    return;
}
function ClearStudyProgramFilter() {
    document.getElementById("studyprogram_input").value = "";
    ShowSelectedModules();
}
studyprogram_idlist = []
studyprogram_textlist = []


function autocomplete_noresults() {
    var sp_suggestions_container = document.getElementById('studyprogram_inputautocomplete-list');
    if(sp_suggestions_container) {
        var n_sp_suggestions = sp_suggestions_container.childElementCount;
        if (n_sp_suggestions===0) {
            no_modules_item = document.createElement("DIV");
            no_modules_item.innerHTML = "Keine Studienprogramme für Module dieses Semesters gefunden.";
            sp_suggestions_container.appendChild(no_modules_item);
        }
    }
}
$('#studyprogram_input').on('input',function(e){
    autocomplete_noresults();
});

function monkeyPatchAutocomplete() {
    // hack: override autocomplete _renderItem to highlight matching part
    $.ui.autocomplete.prototype._renderItem = function (ul, item) {

        // Escape any regex syntax inside this.term
        var cleanTerm = this.term.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');

        // Build pipe separated string of terms to highlight
        var keywords = $.trim(cleanTerm).replace('  ', ' ').split(' ').join('|');

        // Get the new label text to use with matched terms wrapped
        // in a span tag with a class to do the highlighting
        var re = new RegExp("(" + keywords + ")", "gi");
        var output = item.label.replace(re,  
            '<span class="ui-menu-item-highlight">$1</span>');

        return $("<li>")
            .append($("<a>").html(output))
            .appendTo(ul);
    };
    // hack: override autocomplete search function compare starts of options ("^")
    $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
            return matcher.test(value.label || value.value || value);
        });
    };
};

$(function () {
    monkeyPatchAutocomplete();
});
