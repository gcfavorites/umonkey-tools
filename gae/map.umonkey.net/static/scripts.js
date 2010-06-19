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

			google.maps.event.addListener(marker, 'click', function() {
				var html = '<p class="name"><span>' + s.name + '</span>' + s.region + '</p><p>';
				if (s.founded)
					html += 'Основано в ' + s.founded + 'г. ';
				if (s.area)
					html += 'Площадь: ' + s.area + 'га. ';
				if (s.families) {
					html += s.families + ' семей';
					if (s.winter)
						html += ', ' + s.winter + ' зимует';
					html += '. ';
				}
				if (s.ownership)
					html += 'Земля в собственность. ';
				if (s.residence)
					html += 'Жилой дом с правом прописки. ';
				if (s.electricity || s.water || s.communication || s.internet) {
					var have = new Array();
					if (s.electricity) have.push('электричество');
					if (s.water) have.push('водопровод');
					if (s.communication) have.push('мобильная связь');
					if (s.internet) have.push('интернет');
					html += 'Есть ' + have.join(', ') + '.';
				}
				html += '</p>';

				if (s.is_open)
					html += '<p>Приём продолжается.</p>';

				var links = new Array();
				addurl(links, s.url);
				addurl(links, s.url_own);
				addurl(links, s.url_vk);
				if (links.length)
					html += '<p>' + links.join(' &middot; ') + '</p>';

				iw.setContent("<div class='pos'>" + html + "</div>");
				iw.open(map, marker);
			});
		}
	} catch (e) {
		alert('Error: ' + e);
	}

	function addurl(ar, url)
	{
		if (url) {
			var u = new URI(url);
			ar.push('<a target="_blank" href="'+ url +'">'+ u.authority +'</a>')
		}
	}
}
