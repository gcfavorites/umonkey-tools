function show_map() {
	try {
		var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(map_data.bounds.latmin, map_data.bounds.lonmin), new google.maps.LatLng(map_data.bounds.latmax, map_data.bounds.lonmax));
		var map = new google.maps.Map(document.getElementById("map_canvas"), {
			zoom: 4,
			center: bounds.getCenter(),
			mapTypeId: google.maps.MapTypeId.HYBRID,
			mapTypeControlOptions: { style: google.maps.MapTypeControlStyle.DROPDOWN_MENU }
		});
		map.panToBounds(bounds);

		var shadow = new google.maps.MarkerImage('static/shadow.png',
			new google.maps.Size(59, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var green = new google.maps.MarkerImage('static/green.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var green_dot = new google.maps.MarkerImage('static/green-dot.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var red = new google.maps.MarkerImage('static/red.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var red_dot = new google.maps.MarkerImage('static/red-dot.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var iw = new google.maps.InfoWindow({
			maxWidth: 300
		});

		for (var idx = 0; idx < map_data.markers.length; idx++) {
			var s = map_data.markers[idx], z, icon;

			if (s.is_open && s.residence) {
				icon = green_dot;
				z = 4;
			} else if (s.is_open) {
				icon = green;
				z = 3;
			} else if (s.residence) {
				icon = red_dot;
				z = 2;
			} else {
				icon = red;
				z = 1;
			}

			add_marker(map, new google.maps.LatLng(s.ll[0], s.ll[1]), icon, shadow, z, s);
		}

		function add_marker(map, position, icon, shadow, z, s)
		{
			var marker = new google.maps.Marker({
				map: map,
				position: position,
				icon: icon,
				shadow: shadow,
				zIndex: z,
				title: s.name
			});

			if (s.html) {
				google.maps.event.addListener(marker, 'click', function() {
					iw.setContent("<div class='pos'>" + s.html + "</div>");
					iw.open(map, marker);
				});
			}
		}
	} catch (e) {
		alert('Error: ' + e);
	}
}
