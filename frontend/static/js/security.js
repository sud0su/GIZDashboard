
    document.addEventListener('DOMContentLoaded', function(){

        // Select All/None
            $('.checkbox-group .parents-checkbox .panel-select-all :checkbox').change(function () {
                $(this).closest('.checkbox-group').find(':checkbox').not(this).prop('checked', this.checked).closest('label');
            });

            $('.child-checkbox :checkbox').change(function () {
                var $group = $(this).closest('.checkbox-group');
                $group.find('.parents-checkbox .panel-select-all :checkbox').prop('checked', !$group.find('.child-checkbox :checkbox:not(:checked)').length);
            });
        // /Select All/None

        // DateRangePicker
        var daterange = getParameterByName("daterange");
        if (daterange == null){
            var start = moment().subtract(365, 'days');
            var end = moment();
        } else {
            var dateVar = daterange.split(',');
            var start = moment(new Date(dateVar[0].substr(0, 4), parseInt(dateVar[0].substr(5, 2))-1, dateVar[0].substr(8, 2)));
            var end = moment(new Date(dateVar[1].substr(0, 4), parseInt(dateVar[1].substr(5, 2))-1, dateVar[1].substr(8, 2)));;
        }

        function cb(start, end) {
            $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }

        $('#reportrange').daterangepicker({
            startDate: start,
            endDate: end,
            ranges: {
            '{% trans 'Today' %}': [moment(), moment()],
            '{% trans 'Yesterday' %}': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            '{% trans 'Last 7 Days' %}': [moment().subtract(6, 'days'), moment()],
            '{% trans 'Last 30 Days' %}': [moment().subtract(29, 'days'), moment()],
            '{% trans 'This Month' %}': [moment().startOf('month'), moment().endOf('month')],
            '{% trans 'Last Month' %}': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
            '{% trans 'Last Year' %}': [moment().subtract(365, 'days'), moment()]
            }
        }, cb);

        cb(start, end);

        $('#reportrange').on('apply.daterangepicker', function(ev, picker) {
            var url = $(location).attr("href");
            if (daterange == null){
            window.document.location = url+'&daterange='+picker.startDate.format('YYYY-MM-DD')+','+picker.endDate.format('YYYY-MM-DD');
            }  else {
            // url = url.replace(/(daterange=).*?(&)/,'$1' + picker.startDate.format('YYYY-MM-DD')+','+picker.endDate.format('YYYY-MM-DD') + '$2');
            url = updateUrlParameter(url, 'daterange', picker.startDate.format('YYYY-MM-DD')+','+picker.endDate.format('YYYY-MM-DD'))

            window.document.location = url;
            }
        });
        // /DateRangePicker

        $( "form.form-inline" ).submit(function( event ) {
        event.preventDefault();
        });

        $('button.ply-trget').on('click', function(event) {
            var type_selected_param = '';
            var target_selected_param = '';

            var type_unselected = $("input[name='main_type_select[]']:checkbox:not(:checked)");
            var type_selected = $("input[name='main_type_select[]']:checkbox:checked");

            var target_unselected = $("input[name='main_target_select[]']:checkbox:not(:checked)");
            var target_selected = $("input[name='main_target_select[]']:checkbox:checked");

            if (type_unselected.length > 0) {
                // var type_array = type_selected.val();
                var type_array = [];
                type_selected.each( function () {
                type_array.push($(this).val());
                });
                type_selected_param += type_array;
            }


            if (target_unselected.length > 0) {
                // var target_array = $('#incidentTarget-select').val();
                var target_array = [];
                target_selected.each( function () {
                target_array.push($(this).val());
                });
                target_selected_param += target_array
            }

            if (type_selected.length == 0) {
                type_selected_param = 'noselection';
            }

            if (target_selected.length == 0) {
                target_selected_param = 'noselection';
            }

            var url = $(location).attr("href");

            if (type_selected_param != ''){
                if (getParameterByName("incident_type") == null){
                    url += '&incident_type='+type_selected_param;
                } else {
                    url = updateUrlParameter(url, 'incident_type', type_selected_param);
                }

            } else {
                url = removeParam('incident_type', url);
            }

            if (target_selected_param != ''){
                if (getParameterByName("incident_target") == null){
                    url += '&incident_target='+target_selected_param;
                } else {
                    url = updateUrlParameter(url, 'incident_target', target_selected_param)
                }

            } else {
                url = removeParam('incident_target', url);
            }

            window.document.location = url;
        });
    });