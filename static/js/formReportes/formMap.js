  function initMap() {
    const centro = { lat: -33.4489, lng: -70.6693 };
    const map = new google.maps.Map(document.getElementById("map"), {
      center: centro,
      zoom: 13,
      mapTypeControl: false
    });
    const geocoder = new google.maps.Geocoder();
    const marker = new google.maps.Marker({
      position: centro,
      map,
      draggable: true
    });

    marker.addListener("dragend", () => {
      const pos = marker.getPosition();
      fillLatLng(pos);
      geocodeLatLng(pos);
    });

    const input = document.getElementById("id_direccion");
    const autocomplete = new google.maps.places.Autocomplete(input, {
      componentRestrictions: { country: "cl" },
      fields: ["geometry", "formatted_address", "address_components"]
    });
    autocomplete.bindTo("bounds", map);

    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      if (!place.geometry) return;
      map.panTo(place.geometry.location);
      map.setZoom(15);
      marker.setPosition(place.geometry.location);
      fillLatLng(place.geometry.location);
      input.value = place.formatted_address;
      setComuna(place.address_components);
    });

    map.addListener("click", (e) => {
      const latlng = e.latLng;
      marker.setPosition(latlng);
      map.panTo(latlng);
      fillLatLng(latlng);
      geocodeLatLng(latlng);
    });

    function fillLatLng(latlng) {
      document.getElementById("id_latitud").value  = latlng.lat().toFixed(6);
      document.getElementById("id_longitud").value = latlng.lng().toFixed(6);
    }

    function geocodeLatLng(latlng) {
      geocoder.geocode({ location: latlng }, (results, status) => {
        if (status === "OK" && results[0]) {
          input.value = results[0].formatted_address;
          setComuna(results[0].address_components);
        }
      });
    }

    function setComuna(components) {
      // 1) Extraer nombre de comuna
      let comuna = "";
      const prioridades = [
        "sublocality_level_1",
        "locality",
        "administrative_area_level_2"
      ];
      for (let tipo of prioridades) {
        const comp = components.find(c => c.types.includes(tipo));
        if (comp) {
          comuna = comp.long_name;
          break;
        }
      }
      if (!comuna && components.length) {
        comuna = components[0].long_name;
      }

      // 2) Normalizar texto
      const normalize = str =>
        str.normalize("NFD")
           .replace(/[\u0300-\u036f]/g, "")
           .toLowerCase()
           .replace(/\s+/g, "");

      const comunaNorm = normalize(comuna);

      // 3) Encontrar el <select> correcto
      const select =
        document.getElementById("id_comuna") ||
        document.getElementById("id_id_comuna");
      if (!select) {
        console.error("Campo comuna no encontrado (id_comuna o id_id_comuna)");
        return;
      }

      // 4) Asignar la opción que coincida
      Array.from(select.options).forEach(opt => {
        if (normalize(opt.text) === comunaNorm) {
          select.value = opt.value;
        }
      });
    }
  }

  // Google Maps callback
  window.initMap = initMap;