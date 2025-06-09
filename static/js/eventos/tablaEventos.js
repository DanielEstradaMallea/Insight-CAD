    // static/js/eventos/tablaEventos.js

    $(document).ready(function () {
        let hoy = new Date().toISOString().slice(0, 10);
        let hace30 = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
        $('#fechaFin').val(hoy);
        $('#fechaInicio').val(hace30);

        // Inicialización DataTable
        let tablaEventos = $('#tablaEventos').DataTable({
            dom: "<'row mb-3'<'col-md-8'l><'col-md-4 d-flex justify-content-end align-items-center gap-2'Bf>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row mt-2'<'col-md-5'i><'col-md-7'p>>",
            "pageLength": 10,
            "lengthMenu": [5, 10, 20, 50, 100],
            "ordering": false,
            "language": {
                "decimal": "",
                "emptyTable": "No hay datos disponibles en la tabla",
                "info": "Mostrando _START_ a _END_ de _TOTAL_ eventos",
                "infoEmpty": "Mostrando 0 a 0 de 0 eventos",
                "infoFiltered": "(filtrado de _MAX_ eventos en total)",
                "thousands": ",",
                "lengthMenu": "Mostrar _MENU_ eventos",
                "loadingRecords": "Cargando...",
                "processing": "Procesando...",
                "search": "",
                "searchPlaceholder": "Búsqueda rápida...",
                "zeroRecords": "No se encontraron eventos",
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "Siguiente",
                    "previous": "Anterior"
                }
            },
            "columns": [
                {
                    data: 'prioridad', render: function (data) {
                        if (data === "ALTA") return '<span class="badge bg-danger"><i class="fa-solid fa-circle-exclamation me-1"></i>Alta</span>';
                        if (data === "MEDIA") return '<span class="badge bg-warning text-dark"><i class="fa-solid fa-triangle-exclamation me-1"></i>Media</span>';
                        if (data === "BAJA") return '<span class="badge bg-success"><i class="fa-solid fa-arrow-down me-1"></i>Baja</span>';
                        return '<span class="badge bg-secondary">-</span>';
                    }
                },
                { data: 'nombre' },
                { data: 'tipo' },
                { data: 'subtipo' },
                { data: 'fecha' },
                { data: 'comuna' },
                {
                    data: 'estado', render: function (data, type, row) {
                        let estadoClass = '';
                        switch (data) {
                            case 'INGRESADO': estadoClass = 'bg-success text-light'; break;
                            case 'ABIERTO': estadoClass = 'bg-warning text-dark'; break;
                            case 'CERRADO': estadoClass = 'bg-secondary'; break;
                            case 'EN PROCESO': estadoClass = 'bg-danger text-light'; break;
                            default: estadoClass = 'bg-warning';
                        }
                        return `<span class="btn btn-sm btn-estado ${estadoClass}" 
                            data-evento-id="${row.id_evento}" 
                            data-estado-actual="${data}"
                            style="cursor:pointer; font-weight:600; border-radius: 3px;">
                            ${data}
                        </span>`;
                    }
                },
                {
                    data: 'alerta', render: function (data, type, row) {
                        let estado = (data === "SI");
                        return `
                            <button class="btn btn-sm ${estado ? 'btn-danger' : 'btn-secondary'} btn-alerta" 
                                data-evento-id="${row.id_evento}" 
                                data-estado-alerta="${data}">
                                <i class="fa-solid ${estado ? 'fa-bell fa-shake' : 'fa-bell-slash'}"></i> 
                                ${estado ? 'Activa' : 'No'}
                            </button>
                        `;
                    }
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    className: "text-center",
                    render: function (data, type, row) {
                        return `<span class="volt-table-action" data-id="${row.id_evento}" title="Ver detalle" data-bs-toggle="tooltip">
                            <i class="fa-solid fa-eye"></i>
                        </span>`;
                    }
                }
            ],
            "data": [],
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: '<i class="fa-solid fa-file-excel"></i>',
                    className: 'btn btn-volt',
                    titleAttr: 'Exportar Excel'
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fa-solid fa-file-pdf"></i>',
                    className: 'btn btn-volt',
                    orientation: 'landscape',
                    pageSize: 'A4',
                    titleAttr: 'Exportar PDF',
                    customize: function (doc) {
                        doc.styles.tableHeader.fillColor = '#2d3652';
                    }
                },
                {
                    extend: 'print',
                    text: '<i class="fa-solid fa-print"></i>',
                    className: 'btn btn-volt',
                    titleAttr: 'Imprimir'
                }
            ]
        });

        // Llenar tipos de evento y cargar tabla inicial
        $.getJSON(urlCargarTiposEventos, function (data) {
            if (data.length > 0) {
                $('#tipoEventoFilter').empty();
                data.forEach(function (tipo, i) {
                    $('#tipoEventoFilter').append(
                        `<option value="${tipo.id_tipo}"${i === 0 ? ' selected' : ''}>${tipo.nombre}</option>`
                    );
                });
                $('#tipoEventoFilter').val(data[0].id_tipo);
                let tipo = $('#tipoEventoFilter').val();
                cargarEventos(tipo, $('#fechaInicio').val(), $('#fechaFin').val());
            }
        });

        // Filtros con animación en el botón
        $('#btnFiltrar').on('click', function () {
            let tipo = $('#tipoEventoFilter').val();
            let inicio = $('#fechaInicio').val();
            let fin = $('#fechaFin').val();

            $('#btnFiltrar').attr('disabled', true);
            $('#icon-filtrar').hide();
            $('#text-filtrar').text('Cargando...');
            $('#spinner-filtrar').show();

            cargarEventos(tipo, inicio, fin);
        });

        function cargarEventos(tipo, inicio, fin) {
            $.getJSON(urlObtenerEventosFiltrados, {
                tipo_evento: tipo,
                fecha_inicio: inicio,
                fecha_fin: fin,
                page: 1
            }, function (resp) {
                let eventos = [];
                (resp.eventos || resp).forEach(function (e) {
                    eventos.push({
                        id_evento: e.id_evento,
                        nombre: e.nombre,
                        tipo: e.id_tipo__nombre,
                        subtipo: e.id_subtipo__nombre,
                        fecha: e.fecha,
                        comuna: e.id_comuna__nombre,
                        estado: e.id_estado_actual__nombre,
                        alerta: e.alerta_encendida,
                        prioridad: e.id_subtipo__prioridad,
                        detalle: e.detalle,
                        latitud: e.latitud,
                        longitud: e.longitud,
                    });
                });
                tablaEventos.clear().rows.add(eventos).draw();

                $('#btnFiltrar').attr('disabled', false);
                $('#icon-filtrar').show();
                $('#text-filtrar').text('Filtrar');
                $('#spinner-filtrar').hide();
            });
        }

        // Mostrar detalle en Offcanvas y cargar por AJAX
        function limpiarCamposDetalle() {
            $('#detalle-nombre-header').text('-');
            $('#detalle-tipo').text('-');
            $('#detalle-subtipo').text('-');
            $('#detalle-procedencia').text('-');
            $('#detalle-registrado').text('-');
            $('#detalle-direccion').text('-');
            $('#detalle-comuna').text('-');
            $('#detalle-coordenadas').text('-');
            $('#detalle-estado').text('-');
            $('#detalle-fechas').html('-');
            $('#detalle-observaciones').text('-');
            $('#detalle-mapa').html('');
            $('#detalle-imagenes').html('');
            $('#antecedentes-content').html('');
            $('#listaPersonasEvento').html('');
            $('#asignados-lista-personas').html('');
            $('#listaVehiculosEvento').html('');
            $('#asignados-lista-vehiculos').html('');
        }

        $('#tablaEventos tbody').on('click', '.volt-table-action', function () {
            let rowData = $('#tablaEventos').DataTable().row($(this).closest('tr')).data();
            let evento_id = rowData.id_evento;

            limpiarCamposDetalle();

            $('#custom-offcanvas-backdrop').show();
            $('#custom-offcanvas-detalle').addClass('show');
            setTimeout(() => { $('#tab-detalle').tab('show'); }, 120);

            $('#personas-content').data('evento-id', evento_id);
            $('#vehiculos-content').data('evento-id', evento_id);

            // --- CARGAR DETALLES PRINCIPALES ---
            $.getJSON(`/obtener-detalle-evento/${evento_id}/`, function (data) {
                $('#detalle-nombre-header').text(data.nombre || '-');
                $('#detalle-tipo').text(data.tipo || '-');
                $('#detalle-subtipo').text(data.subtipo || '-');
                $('#detalle-procedencia').text(data.procedencia || '-');
                $('#detalle-registrado').text(data.registrado || '-');
                $('#detalle-direccion').text(data.direccion || '-');
                $('#detalle-comuna').text(data.comuna || '-');
                $('#detalle-coordenadas').text((data.latitud && data.longitud) ? data.latitud + ', ' + data.longitud : '-');
                $('#detalle-estado').text(data.estado || '-');
                $('#detalle-fechas').html('Registro: ' + (data.fecha || '-') + '<br>Hora: ' + (data.hora || '-'));
                $('#detalle-observaciones').text(data.detalle || '-');
                let lat = data.latitud, lng = data.longitud;
                if (lat && lng) {
                    $('#detalle-mapa').html('<div id="mini-mapa-evento" style="height:180px; border-radius:12px;"></div>');
                    setTimeout(function () {
                        let latNum = typeof lat === "string" ? parseFloat(lat.replace(',', '.')) : lat;
                        let lngNum = typeof lng === "string" ? parseFloat(lng.replace(',', '.')) : lng;
                        if (!isNaN(latNum) && !isNaN(lngNum)) {
                            let map = L.map('mini-mapa-evento', { scrollWheelZoom: false }).setView([latNum, lngNum], 16);
                            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                attribution: '&copy; OpenStreetMap contributors'
                            }).addTo(map);
                            L.marker([latNum, lngNum]).addTo(map).bindPopup('Ubicación evento');
                        } else {
                            $('#mini-mapa-evento').replaceWith('<div class="alert alert-warning m-3">Coordenadas inválidas</div>');
                        }
                    }, 120);
                } else {
                    $('#detalle-mapa').html(`<div class="alert alert-secondary text-center mb-0 py-3">
                        <i class="fa-solid fa-map-location-dot fa-lg mb-2"></i><br>Sin coordenadas para mostrar el mapa
                    </div>`);
                }
            });

            // Imágenes
            $.getJSON(`/obtener-imagenes-evento/${evento_id}/`, function (data) {
                let imgs = '';
                if (data.imagenes && data.imagenes.length > 0) {
                    data.imagenes.forEach((img, idx) => {
                        imgs += `
                            <div class="col-4 mb-3">
                                <img src="${img.url}" alt="${img.nombre}" title="${img.nombre}" 
                                    class="img-fluid rounded shadow-sm img-evento-thumb" 
                                    style="cursor:pointer;object-fit:cover;width:100%;max-height:140px;" 
                                    data-img-url="${img.url}">
                            </div>`;
                    });
                } else {
                    imgs = `<div class="col-12 text-center text-muted py-4">
                        <i class="fa-regular fa-image fa-2x mb-2"></i><br>
                        <span>Sin imágenes asociadas</span>
                    </div>`;
                }
                $('#detalle-imagenes').html(imgs);

                $('.img-evento-thumb').on('click', function () {
                    $('#imgModalGrande').attr('src', $(this).data('img-url'));
                    $('#modalImagenGrande').modal('show');
                });
            });

            // Antecedentes
            function cargarAntecedentes() {
                $.getJSON(`/obtener-antecedentes/${evento_id}/`, function (data) {
                    let html = `
                        <form id="form-antecedente" class="mb-4">
                            <div class="mb-3">
                                <label for="input-antecedente" class="fw-semibold">Antecedente:</label>
                                <textarea class="form-control" id="input-antecedente" name="antecedente" rows="2"></textarea>
                            </div>
                            <div class="row mb-3">
                                <div class="col">
                                    <label class="fw-semibold">Fecha:</label>
                                    <input type="date" name="fecha" id="input-fecha" class="form-control" value="${new Date().toISOString().slice(0, 10)}">
                                </div>
                                <div class="col">
                                    <label class="fw-semibold">Hora:</label>
                                    <input type="time" name="hora" id="input-hora" class="form-control" value="${new Date().toTimeString().slice(0, 5)}">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">Guardar</button>
                        </form>
                        <h6 class="mt-3 mb-2 fw-bold">Bitácora de Antecedentes</h6>
                        <div>`;
                    if ((data.antecedentes || []).length === 0) {
                        html += `<div class="alert alert-secondary text-center mb-0">Sin antecedentes registrados</div>`;
                    } else {
                        data.antecedentes.forEach(a => {
                            html += `<div class="bg-light rounded-3 border px-3 py-2 mb-2 small">
                                <span class="fw-semibold">${a.fecha || ''} ${a.hora || ''}</span>
                                <span class="text-muted float-end">Usuario: ${a.id_usuario || '-'}</span><br>
                                ${a.antecedente || ''}
                            </div>`;
                        });
                    }
                    html += '</div>';
                    $('#antecedentes-content').html(html);

                    $('#form-antecedente').off('submit').on('submit', function (e) {
                        e.preventDefault();
                        $.ajax({
                            url: `/guardar-antecedente/${evento_id}/`,
                            type: 'POST',
                            data: $(this).serialize(),
                            headers: { 'X-CSRFToken': window.csrf_token || '' }, // Ajusta según tu contexto
                            success: function (resp) {
                                if (resp.success) {
                                    cargarAntecedentes();
                                } else {
                                    alert(resp.error || 'Error al guardar');
                                }
                            }
                        });
                    });
                });
            }

            cargarAntecedentes();
            $('#tab-antecedentes').off('show.bs.tab').on('show.bs.tab', function () {
                cargarAntecedentes();
            });
        });

        // Cerrar offcanvas
        $('#cerrarDetalleEvento, #custom-offcanvas-backdrop').on('click', function () {
            $('#custom-offcanvas-backdrop').hide();
            $('#custom-offcanvas-detalle').removeClass('show');
            limpiarCamposDetalle();
        });
    });
