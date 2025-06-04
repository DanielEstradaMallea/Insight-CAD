$(document).ready(function () {
    // Elementos del DOM (ajustados a tus IDs)
    const buscarPatente = document.getElementById('buscarPatenteVehiculo');
    const buscarModelo = document.getElementById('buscarModeloVehiculo');
    const btnBuscar = document.getElementById('btnBuscarVehiculoEvento');
    const listaVehiculos = document.getElementById('listaVehiculosEvento');
    let currentEventoId = null;

    // Helper para CSRF (Django)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Helper: Obtiene el evento ID del atributo data o variable global
    function getEventoId() {
        // El atributo data-evento-id DEBE estar en el div del tab (vehiculos-content)
        let id = $('#vehiculos-content').data('evento-id');
        if (!id) id = window.currentEventoId;
        return id;
    }

    // Mostrar vehículos ya asociados al evento
    function cargarVehiculosAsignados(eventoId) {
        fetch(`/obtener-vehiculos-evento/?evento_id=${eventoId}`)
            .then(r => r.json())
            .then(data => {
                const tbody = document.getElementById("asignados-lista-vehiculos");
                tbody.innerHTML = "";
                if (!data.success || data.data.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="5">No hay vehículos asignados aún.</td></tr>`;
                    return;
                }
                data.data.forEach(vehiculo => {
                    let row = `<tr>
                        <td>${vehiculo.patente}</td>
                        <td>${vehiculo.marca || '-'}</td>
                        <td>${vehiculo.modelo || '-'}</td>
                        <td>${vehiculo.tipo || '-'}</td>
                        <td><!-- Futuro: botón eliminar --></td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            })
            .catch(() => {});
    }

    // Renderizar vehículos encontrados en búsqueda
    function renderizarVehiculos(vehiculos) {
        listaVehiculos.innerHTML = '';
        if (!vehiculos.length) {
            listaVehiculos.innerHTML = `<tr><td colspan="5">No se encontraron vehículos.</td></tr>`;
            return;
        }
        vehiculos.forEach(vehiculo => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${vehiculo.patente}</td>
                <td>${vehiculo.marca || '-'}</td>
                <td>${vehiculo.modelo || '-'}</td>
                <td>${vehiculo.color || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-success btn-asignar-vehiculo" data-vehiculo-id="${vehiculo.id_vehiculo}">
                        <i class="fas fa-car-plus"></i> Asignar
                    </button>
                </td>
            `;
            // Botón asignar
            const btn = tr.querySelector('.btn-asignar-vehiculo');
            btn.addEventListener('click', () => {
                const vehiculoId = btn.dataset.vehiculoId;
                const eventoId = getEventoId();
                if (!eventoId) {
                    alert("No se pudo obtener el ID del evento.");
                    return;
                }
                fetch('/registrar-vehiculo/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        vehiculo_id: vehiculoId,
                        evento_id: eventoId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.innerHTML = '<i class="fas fa-check"></i> Asignado';
                        btn.classList.replace('btn-success', 'btn-secondary');
                        btn.disabled = true;
                        cargarVehiculosAsignados(eventoId);
                    } else {
                        throw new Error(data.error || 'Error desconocido');
                    }
                })
                .catch(error => {
                    alert(error.message);
                });
            });
            listaVehiculos.appendChild(tr);
        });
    }

    // Buscar vehículos SOLO cuando presionas el botón buscar
    btnBuscar.addEventListener('click', function () {
        const params = new URLSearchParams({
            patente: buscarPatente.value,
            modelo: buscarModelo.value
        });
        fetch(`/api/buscar-vehiculos/?${params}`)
            .then(r => r.json())
            .then(renderizarVehiculos)
            .catch(() => alert('Error buscando vehículos'));
    });

    // Detectar cambio de pestaña (tab) para recargar los asignados
    $('#tab-vehiculos').on('shown.bs.tab', function () {
        // Cuando abres la pestaña Vehículos
        // Busca el id_evento desde el detalle
        const idEvento = $('#custom-offcanvas-detalle').data('evento-id');
        // O desde el tab-content data
        $('#vehiculos-content').data('evento-id', idEvento);
        currentEventoId = idEvento;
        if (idEvento) cargarVehiculosAsignados(idEvento);
    });

    // También recarga si abres el detalle directo (por seguridad)
    $(document).on('show.bs.offcanvas', '#custom-offcanvas-detalle', function () {
        const idEvento = $('#custom-offcanvas-detalle').data('evento-id');
        $('#vehiculos-content').data('evento-id', idEvento);
        currentEventoId = idEvento;
        if ($('#tab-vehiculos').hasClass('active')) {
            if (idEvento) cargarVehiculosAsignados(idEvento);
        }
    });
});
