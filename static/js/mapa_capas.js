
let map, heatmap, trafficLayer;
let eventsLoader = document.getElementById('events-loader');

const sinLugares = { featureType:"poi", elementType:"labels", stylers:[{ visibility:"off" }] };
const darkStyle = [ { elementType:"geometry", stylers:[{ color:"#121212" }] }, { elementType:"labels.icon", stylers:[{ visibility:"off" }] }, { elementType:"labels.text.fill", stylers:[{ color:"#e0e0e0" }] }, { elementType:"labels.text.stroke", stylers:[{ color:"#000000" }] } ];
const retroStyle = [ { elementType:"geometry", stylers:[{ color:"#ebe3cd" }] }, { elementType:"labels.text.fill", stylers:[{ color:"#523735" }] }, { elementType:"labels.text.stroke", stylers:[{ color:"#f5f1e6" }] } ];

function updateMapLayers() {
  const selectedStyle = document.querySelector('input[name="mapStyle"]:checked').value;
  if(selectedStyle === 'default'){
    map.setOptions({ styles:[sinLugares] }); map.setMapTypeId('roadmap');
  } else if(selectedStyle === 'dark'){
    map.setOptions({ styles: darkStyle }); map.setMapTypeId('roadmap');
  } else if(selectedStyle === 'retro'){
    map.setOptions({ styles: retroStyle }); map.setMapTypeId('roadmap');
  } else if(selectedStyle === 'satellite'){
    map.setOptions({ styles: [sinLugares] }); map.setMapTypeId('satellite');
  }
  if(document.getElementById('trafficSwitch').checked) {
    trafficLayer.setMap(map);
  } else {
    trafficLayer.setMap(null);
  }
  if(document.getElementById('heatmapSwitch').checked && heatmap) {
    heatmap.setMap(map);
  } else if (heatmap) {
    heatmap.setMap(null);
  }
}

function getCustomMarkerIcon(color = "#888") {
  const svg = `<svg width="32" height="48" viewBox="0 0 32 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="16" cy="16" rx="12" ry="12" fill="${color}"/>
    <path d="M16 47C16 47 29 29 16 29C3 29 16 47 16 47Z" fill="${color}"/>
    <circle cx="16" cy="16" r="6" fill="#fff"/>
  </svg>`;
  return {
    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
    scaledSize: new google.maps.Size(32, 48),
    anchor: new google.maps.Point(16, 47)
  };
}

function pieChartSVG(colors, counts, size=48) {
  const total = counts.reduce((a,b)=>a+b,0);
  if(colors.length===1){
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2}" fill="${colors[0]}"/>
      <circle cx="${size/2}" cy="${size/2}" r="${size/2-3}" fill="none" stroke="#fff" stroke-width="3"/>
    </svg>`;
  }
  let angle=0, paths='';
  for(let i=0;i<colors.length;i++){
    const slice = counts[i]/total*2*Math.PI;
    const x1 = size/2 + (size/2)*Math.cos(angle);
    const y1 = size/2 + (size/2)*Math.sin(angle);
    angle += slice;
    const x2 = size/2 + (size/2)*Math.cos(angle);
    const y2 = size/2 + (size/2)*Math.sin(angle);
    const largeArc = slice>Math.PI?1:0;
    paths += `<path d="M${size/2},${size/2} L${x1},${y1} A${size/2},${size/2} 0 ${largeArc} 1 ${x2},${y2} z" fill="${colors[i]}"/>`;
  }
  paths += `<circle cx="${size/2}" cy="${size/2}" r="${size/2-3}" fill="none" stroke="#fff" stroke-width="3"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${paths}</svg>`;
}

function bounceMarker(marker, amp=10, speed=350) {
  const orig = marker.getPosition();
  let up=true;
  setInterval(()=>{
    marker.setPosition(new google.maps.LatLng(
      orig.lat() + (up? amp*1e-5 : 0),
      orig.lng()
    ));
    up=!up;
    if(!up) marker.setPosition(orig);
  }, speed);
}

window.initMap = function() {
  map = new google.maps.Map(document.getElementById('map'), {
    center:{lat:-33.4489,lng:-70.6693}, zoom:11, mapTypeControl:false, streetViewControl:false
  });

  trafficLayer = new google.maps.TrafficLayer();
  heatmap = null;

  // Buscador Google Places
  const ac = new google.maps.places.Autocomplete(
    document.getElementById('pac-input'),
    { fields:["geometry","name"], types:["geocode","establishment"] }
  );
  ac.bindTo('bounds', map);
  ac.addListener('place_changed', ()=>{
    const p = ac.getPlace();
    if (p.geometry?.location) {
      map.panTo(p.geometry.location);
      map.setZoom(16);
    }
  });

  document.querySelectorAll('input[name="mapStyle"]').forEach(radio => {
    radio.addEventListener('change', updateMapLayers);
  });
  document.getElementById('trafficSwitch')?.addEventListener('change', updateMapLayers);
  document.getElementById('heatmapSwitch')?.addEventListener('change', updateMapLayers);

  // Eventos
  eventsLoader.style.display = "flex";
  fetch('/eventos/')
    .then(r=>r.json())
    .then(eventos=>{
      const colorBy = p=>{
        if(p==='ALTA') return '#dc3545';
        if(p==='MEDIA') return '#FFD700';
        if(p==='BAJA') return '#198754';
        return '#888';
      };

      const markers = eventos.map(e=>{
        const lat = parseFloat(e.latitud),
              lng = parseFloat(e.longitud);
        if(isNaN(lat)||isNaN(lng)) return null;
        const mk = new google.maps.Marker({
          map,
          position: { lat, lng },
          icon: getCustomMarkerIcon(colorBy(e.id_subtipo__prioridad))
        });
        bounceMarker(mk);
        return mk;
      }).filter(Boolean);

      new markerClusterer.MarkerClusterer({
        map, markers,
        renderer:{
          render({count, markers, position}){
            const stats = {};
            markers.forEach(m=>{
              const match = decodeURIComponent(m.getIcon().url)
                              .match(/fill="(#[A-Fa-f0-9]{3,6})"/);
              const c = match ? match[1] : '#888';
              stats[c] = (stats[c]||0)+1;
            });
            const cols = Object.keys(stats), cnts = Object.values(stats);
            const svg = pieChartSVG(cols, cnts, 48);

            const cl = new google.maps.Marker({
              position,
              icon: {
                url: 'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(svg),
                scaledSize: new google.maps.Size(48,48),
                anchor: new google.maps.Point(24,24)
              },
              label: {
                text: String(count),
                color:'#fff', fontWeight:'bold', fontSize:'14px'
              },
              zIndex: google.maps.Marker.MAX_ZINDEX + count
            });

            const info = new google.maps.InfoWindow({
              content: `<div style="min-width:120px;font-size:14px;">
                Total: ${count}<br>` +
                cols.map((c,i)=>
                  `<span style="display:inline-block;width:0.8em;height:0.8em;
                                 background:${c};border-radius:50%;
                                 margin-right:0.3em;"></span>${cnts[i]}`
                ).join('<br>') +
              `</div>`
            });
            cl.addListener('mouseover', ()=> info.open(map,cl));
            cl.addListener('mouseout', ()=> info.close());
            return cl;
          }
        }
      });

      // Generar heatmap data si está activado
      if (document.getElementById('heatmapSwitch').checked) {
        const heatmapData = eventos
          .filter(e=>!isNaN(parseFloat(e.latitud)) && !isNaN(parseFloat(e.longitud)))
          .map(e=>({
            location: new google.maps.LatLng(parseFloat(e.latitud),parseFloat(e.longitud)),
            weight: e.id_subtipo__prioridad === 'ALTA' ? 7 : e.id_subtipo__prioridad === 'MEDIA' ? 3 : 1
          }));
        heatmap = new google.maps.visualization.HeatmapLayer({ data: heatmapData, radius: 55 });
        heatmap.setMap(map);
      }
    })
    .finally(()=>{
      setTimeout(()=>{ eventsLoader.style.display = "none"; }, 400);
    });
};
