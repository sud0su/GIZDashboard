function jump_url(code){
	var url = window.location.href;

	if (getParameterByName("code") == null){
		url += '&code='+code;
	} else {
		url = updateUrlParameter(url, 'code', code)
	}

	if (code == 0){
		url = removeParam('code', url)
	}

	window.document.location = url;

}

function getParameterByName(name, url) {
	if (!url) url = window.location.href;
	name = name.replace(/[\[\]]/g, "\\$&");
	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
		results = regex.exec(url);
	if (!results) return null;
	if (!results[2]) return '';
	return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function removeParam(key, sourceURL) {
	var rtn = sourceURL.split("?")[0],
		param,
		params_arr = [],
		queryString = (sourceURL.indexOf("?") !== -1) ? sourceURL.split("?")[1] : "";
	if (queryString !== "") {
		params_arr = queryString.split("&");
		for (var i = params_arr.length - 1; i >= 0; i -= 1) {
			param = params_arr[i].split("=")[0];
			if (param === key) {
				params_arr.splice(i, 1);
			}
		}
		rtn = rtn + "?" + params_arr.join("&");
	}
	return rtn;
}

function updateUrlParameter(url, param, value){
	param = encodeURIComponent(param);
	var r = "([&?]|&amp;)" + param + "\\b(?:=(?:[^&#]*))*";
	var a = document.createElement('a');
	var regex = new RegExp(r);
	var str = param + (value ? "=" + encodeURIComponent(value) : ""); 
	a.href = url;
	var q = a.search.replace(regex, "$1"+str);
	if (q === a.search) {
		a.search += (a.search ? "&" : "") + str;
	} else {
		a.search = q;
	}
	console.log(a.href);
	
	return a.href;
}

var _checked = [];

function removeA(arr) {
	var what, a = arguments, L = a.length, ax;
	while (L > 1 && arr.length) {
		what = a[--L];
		while ((ax= arr.indexOf(what)) !== -1) {
			arr.splice(ax, 1);
		}
	}
	return arr;
}

function init_select2_region(){
	if (typeof select2_region === "function") { 
		select2_region();
	}
}

// Humanizer
function humanizeFormatter(value){
	// console.log(value)
	var v= value;
	if(v>=1000 && v<1000000){
		return (parseFloat((v/1000).toPrecision(3)))+' K'
		// return (parseFloat((v/1000).toFixed(1)))+' K'
	}
	else if (v>=1000000 && v<1000000000) {
		return (parseFloat((v/1000000).toPrecision(3)))+' M'
		// return (parseFloat((v/1000000).toFixed(1)))+' M'
	}else{
		if (v==null || isNaN(parseFloat(v))) {
			v=0;
		}
		// console.log(parseFloat((v).toPrecision(3)));
		return (parseFloat((v*1).toPrecision(3)))
		// return (parseFloat((v).toFixed(1)))
	}
}

// Datatables
function init_datatable(){
	$.fn.dataTable.moment( 'MMM D, YYYY' );

	$('.print').DataTable({
		"ordering": false, //do this when print
		"paging": false, //do this when print
		"info": false, //do this when print
		"searching": false, //do this when print
		dom: 't', //do this when print

		"columnDefs": [{
			"render": function (data, type, row){
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"targets": 'hum'
		}],

		"initComplete": function(settings, json) {
			var api = this.api();
			var colLength = api.columns().count();

			for (i = 1; i < colLength; i++) {
				this_footer = $(api.column(i).footer());
				dispData = humanizeFormatter(this_footer.html());
				if(this_footer.attr('class') == 'hum'){
					this_footer.html(dispData);
				}
			}
		}
	});

	$('.online').DataTable({
		dom: 'Bfrtip',
		// pagingType: "full_numbers",
		buttons: [
			{
				extend: "copy",
				className: "btn btn-default btn-sm"
			},
			// {
			// 	extend: "csv",
			// 	filename: 'GIZ Data',
			// 	className: "btn btn-default btn-sm"
			// },
			{
				extend: "excel",
				filename: 'GIZ Data',
				className: "btn btn-default btn-sm"
			},
			{
				extend: "print",
				filename: 'GIZ Data',
				// customize: 
				// 	function ( win ) {
	      //               $(win.document.body)
	      //                   .css( 'font-size', '10pt' )
	      //                   .prepend(
	      //                   	'<img src="static/v2/images/usaid-logo.png" style="position:absolute; top:0; left:0;" />')
	      //                   .prepend(
	      //                       '<img src="static/v2/images/iMMAP.png" style="position:absolute; top:0; left:220px;" />'
	      //                   );
	 
	      //               $(win.document.body).find( 'table' )
	      //                   .addClass( 'compact' )
	      //                   .css( 'font-size', 'inherit' );
	      //           },
				className: "btn btn-default btn-sm"
			}
			// {
			//   extend: "colvis"
			//   className: "btn-sm"
			// }
		],

		"columnDefs": [{
			"render": function (data, type, row){
				// console.log(type);
				// console.log(data);
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"cellType": "th",
			"targets": 'hum'
		}],

		"initComplete": function(settings, json) {
			var api = this.api();
			var colLength = api.columns().count();

			for (i = 1; i < colLength; i++) {
				this_footer = $(api.column(i).footer());
				dispData = humanizeFormatter(this_footer.html());
				console.log(this_footer);
				console.log(this_footer.attr('class'));
				console.log(dispData);
				if(this_footer.attr('class') == 'hum'){
					console.log(this_footer);
					this_footer.html(dispData);
				}
			}
		}
	});

	$('.online_security').DataTable({
		"ordering": false,
		// "pageLength": 30,
		dom: 'Bfrtip',
		buttons: [
			{
				extend: "copy",
				className: "btn btn-default btn-sm"
			},
			// {
			// 	extend: "csv",
			// 	className: "btn btn-default btn-sm"
			// },
			{
				extend: "excel",
				className: "btn btn-default btn-sm"
			},
			{
				extend: "print",
				className: "btn btn-default btn-sm"
			},
			// {
			//   extend: "colvis"
			//   className: "btn btn-default btn-sm"
			// }
		],

		"columnDefs": [{
			"render": function (data, type, row){
				if (type == 'display') {return humanizeTableFormatter(data);}
				return data;
			},
			"targets": 'hum'
		}]
	});
}

function init_chart2(){
	// colorBarDefault= ["#CF000F"];
	// colorBarOther= ['#b40002', '#f1000f', '#ff5c3c', '#ffb89c', '#ffe4d7' ];
	// colorDefault = ['#ffaaab', '#ff6264', '#d13c3e', '#b92527'];

	colorDefault = ['#ff4d6b', '#ffde73', '#8e32e9', '#38ce3c', '#1bdbe0'];

	colorChart={
		'colorDefault': colorDefault,
		'colorBar': colorDefault,
		'colorPolar': colorDefault
	}

	function pie_label() {
		if (this.y > 0){
			// return '<b>' + this.key + '</b> : ' + humanizeFormatter(this.y) + '<br/>(' + Highcharts.numberFormat(this.percentage, 2) + '%)';
			return humanizeFormatter(this.y) + '<br/>(' + Highcharts.numberFormat(this.percentage, 2) + '%)';
		}
	}

	Highcharts.theme = {
		chart: {
			style: {
				fontFamily: '"Arial", Verdana, sans-serif'
			}
		},
		title: {
			text: null,
			verticalAlign: 'bottom',
			style: {
				color: '#424242',
				font: 'bold 13px "Trebuchet MS", Verdana, sans-serif'
			}
		},
		subtitle: {
			style: {
				color: '#424242'
			}
		},
		yAxis: {
			labels: {
				overflow: 'justify'
			},
			title: {
				align: 'high',
			}
		},
		legend: {
			enabled: true
		},
		credits: {
			enabled: false
		}
	};

	// Apply the theme
	Highcharts.setOptions(Highcharts.theme);

	// Object Bar chart
	function bar_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_val, title_val, show_title_val){
		$(id_val).highcharts({
			chart: {
				type: 'bar'
			},
			title: {
				text: title_val,
				style: {
					display: show_title_val
				}
			},
			xAxis: {
				categories: y_title
			},
			yAxis: {
				title: {
					text: x_title
				},
				type: 'logarithmic'
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{
				enabled: legend_val
			},
			plotOptions:{
				series: {
					animation: false
				},
				bar: {
					colorByPoint: colorPoint_val,
					dataLabels: {
						enabled: true,
						formatter: function() {
							return humanizeFormatter(this.y);
						}
					}
				}
			},
			colors: color_val,
			series: data_val
		});
	}

	// Object Donut chart
	function donut_chart(id_val, color_val, data_val, title_val, show_title_val){
		$(id_val).highcharts({
			chart: {
				type: 'pie'
			},
			title: {
				text: title_val,
				style: {
					display: show_title_val
				}
			},
			tooltip: {
				formatter: pie_label
			},
			legend:{
				floating: true,
				align: 'left',
				verticalAlign: 'top',
				layout: 'vertical'
			},
			colors: color_val,
			series: [{
				name: 'Donut',
				data: data_val,
				dataLabels:{
					connectorPadding: 0,
					padding: 0,
					distance: -50,
					connectorShape: 'straight',
					// crookDistance: '70%',
					formatter: pie_label
				},
				size: '110%',
				innerSize: '70%',
				showInLegend:true
			}]
		});
	}

	// Object Stacked Bar chart
	function polar_chart(id_val, color_val, data_title, data_val){
		$(id_val).highcharts({
			chart: {
				polar: true
			},
			xAxis: {
				categories: data_title
			},
			yAxis: {
				type: 'logarithmic',
				tickInterval: 1,
				title: {
					enabled: false
				}
			},
			tooltip: {
				formatter: function() {
					console.log(this);
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{

			},
			plotOptions: {
				series: {
					animation: false
				},
				
			},
			colors: color_val,
			series: data_val
			
		});
	}

	// Object Spline Chart
	function spline_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_val, title_val, show_title_val){
		$(id_val).highcharts('StockChart',{
			rangeSelector: {
				selected: 5,
			},

			xAxis: {
				type: 'datetime',
				minTickInterval: moment.duration(1, 'month').milliseconds(),
				labels: {
					rotation: 35
				}
			},

			time:{
				useUTC: false,
			},

			tooltip: {
				split: true,
				// crosshairs: true,
				formatter: function() {
					var s = [];

					console.log(this);
					s.push(Highcharts.dateFormat('%A, %b %e, %Y %H:%M', this.x));   // Use UTC
					// s.push(moment(this.x).format("YYYY-MM-DD HH:mm a"));            // Use Local Time

					this.points.forEach(function(point) {
						s.push('<b>' + point.series.name + '</b>: ' + point.y);
					});

					return s;
				},
			},
			legend:{
				enabled: legend_val
			},
			colors: color_val,
			series: data_val
		});

		$( ".highcharts-range-selector" ).addClass( "browser-default" );
	}


	$('.spline-chart').each(function(){
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		spline_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, data_chart, title_chart, show_title_chart);

	});

	$('.bar-chart').each(function(){
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		bar_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, data_chart, title_chart, show_title_chart);

	});

	$('.donut-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		// var color_chart = $(id_chart).data("color");
		var data_chart = $(id_chart).data("val");
		// id_chart.attr('data-chart');
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);

		donut_chart(id_chart, selected_color, data_chart, title_chart, show_title_chart);

	});

	$('.polar-chart').each(function(){
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var xAxis_chart = $(id_chart).data("xaxis");

		selected_color = colorChart[color_chart];

		var isi_fix = [];
		for (i = 0; i < data_chart.length; i++) { 
			var isi = {
				name: data_chart[i].type,
				type: 'scatter',
				data: data_chart[i].data.map(function (p) {
					var radius = Math.log(p)*1.5;
					return {
						y: p,
						marker: {
							radius: (radius),
							symbol: 'circle'
						}
					}
				})
			}

			isi_fix.push(isi);
		}
		polar_chart(id_chart, selected_color, xAxis_chart, isi_fix);

	});
}

$(document).ready(function(){
	init_select2_region();
	init_datatable();
	init_chart2();

	$('button#pdf').on('click', function(event) {
		var url = $(location).attr("href");
		// $(".se-pre-con").fadeIn("slow");
		window.document.location = url+'&pdf=true';
		// $(".se-pre-con").fadeOut("slow");
	});

	$('button#csv').on('click', function(event) {
		var url = $(location).attr("href");
		window.document.location = url+'&csv=true';
	});
});