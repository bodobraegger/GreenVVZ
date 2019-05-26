function FlagSelectedSemester() {
    var year_semester = $("option:selected").val();
    // if all semesters are selected, look for year_semester tags containing a space (all do)
    if($("option:selected").val() == 'all') year_semester=" ";
    $('[data-semester]').removeClass('selected-semester');
    $(`[data-semester*="${year_semester}"]`).addClass('selected-semester');
    return;
}
function FlagSelectedStudyprogram() {
    var studyprogram_index = studyprogram_textlist.indexOf(document.getElementById("studyprogram_input").value);
    if(studyprogram_index == -1) {
        document.getElementById("studyprogram_input").value ? console.log("invalid input: " + document.getElementById("studyprogram_input").value) : "";
        $('#whitelist_body').find($(`[data-semester]`)).addClass('selected-studyprogram');
        return;
    }
    studyprogram_id = studyprogram_ids[studyprogram_index];
    var module_ids = studyprogramid_moduleids[studyprogram_id];
    var modules_to_unflag = $('#whitelist_body').find($(`[data-semester]`));
    
    for(i = 0; i < module_ids.length; i++) {
        modules_to_unflag = modules_to_unflag.not($(`#module_${module_ids[i]}`));
        $(`#module_${module_ids[i]}`).addClass('selected-studyprogram');
    }
    $(modules_to_unflag).removeClass('selected-studyprogram');
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
studyprograms = {}
studyprogram_ids = Object.keys(studyprograms)
studyprogram_textlist = Object.keys(studyprograms).map(function(key){
    return studyprograms[key];
});