$(document).ready(function () {
    // Variables para los selects y botones
    const buscarRut = document.getElementById('buscarRutPersona');
    const buscarNombre = document.getElementById('buscarNombrePersona');
    const btnBuscar = document.getElementById('btnBuscarPersonaEvento');
    const listaPersonas = document.getElementById('listaPersonasEvento');
    let tiposPersonas = [];
    let currentEventoId = null;

    // Obtén el evento ID del atributo de la pestaña activa (ajusta si lo guardas en otro lado)
    function getEventoId() {
        // Usa el atributo data-evento-id del contenedor de la pestaña
        return $('#personas-content').data('evento-id') || window.currentEventoId || null;
    }

    // Cargar tipos de persona solo una vez (mejor rendimiento)
    function cargarTiposPersonas(callback) {
        if (tiposPersonas.length > 0) {
            if (typeof callback === 'function') callback();
            return;
        }
        fetch('/tipos-personas/json/')  // AJUSTA ESTA URL según tu sistema de rutas
            .then(r => r.json())
            .then(data => {
                tiposPersonas = data;
                if (typeof callback === 'function') callback();
            })
            .catch(() => alert('Error cargando tipos de personas'));
    }

    // Renderizar resultados de búsqueda
    function renderizarPersonas(personas) {
        listaPersonas.innerHTML = '';
        if (!personas.length) {
            listaPersonas.innerHTML = `<tr><td colspan="4">No se encontraron personas.</td></tr>`;
            return;
        }
        personas.forEach(persona => {
            const tr = document.createElement('tr');
            const selectHTML = tiposPersonas.map(tipo =>
                `<option value="${tipo.id_tipo_persona}">${tipo.nombre}</option>`
            ).join('');
            tr.innerHTML = `
                <td>${persona.rut}</td>
                <td>${persona.nombre} ${persona.paterno || ''} ${persona.materno || ''}</td>
                <td>
                    <select class="form-select tipo-persona">
                        <option disabled value="" selected>Seleccione...</option>
                        ${selectHTML}
                    </select>
                </td>
                <td>
                    <button class="btn btn-sm btn-success btn-asignar" disabled>
                        <i class="fas fa-user-plus"></i> Asignar
                    </button>
                </td>
            `;
            const btn = tr.querySelector('.btn-asignar');
            const select = tr.querySelector('.tipo-persona');
            btn.dataset.personaId = persona.id;

            select.addEventListener('change', () => {
                btn.disabled = !select.value;
            });

            btn.addEventListener('click', () => {
                const personaId = btn.dataset.personaId;
                const tipoPersonaId = select.value;
                const eventoId = getEventoId();
                if (!tipoPersonaId || !eventoId) {
                    alert("Debe seleccionar tipo de persona y tener evento activo.");
                    return;
                }
                // CSRF para Django
                function getCookie(name) {
                    const value = `; ${document.cookie}`;
                    const parts = value.split(`; ${name}=`);
                    if (parts.length === 2) return parts.pop().split(';').shift();
                }
                fetch('/registrar-persona/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        persona_id: personaId,
                        tipo_persona_id: tipoPersonaId,
                        evento_id: eventoId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.innerHTML = '<i class="fas fa-check"></i> Asignado';
                        btn.classList.replace('btn-success', 'btn-secondary');
                        btn.disabled = true;
                        select.disabled = true;
                        $('#mensajeIngresoPersona').fadeIn(300).delay(1200).fadeOut(300);
                        cargarPersonasAsignadas(eventoId);
                    } else {
                        throw new Error(data.error || 'Error desconocido');
                    }
                })
                .catch(error => {
                    alert(error.message);
                });
            });

            listaPersonas.appendChild(tr);
        });
    }

    // Buscar personas (nombre o rut)
    btnBuscar.addEventListener('click', function() {
        cargarTiposPersonas(() => {
            const params = new URLSearchParams({
                nombre: buscarNombre.value,
                rut: buscarRut.value
            });
            fetch(`/personas/buscar/?${params}`)
                .then(r => r.json())
                .then(renderizarPersonas)
                .catch(() => alert('Error buscando personas'));
        });
    });

    // Mostrar personas ya asociadas al evento
    function cargarPersonasAsignadas(eventoId) {
        fetch(`/api/obtener_personas_evento/?evento_id=${eventoId}`)
            .then(r => r.json())
            .then(data => {
                const tbody = document.getElementById("asignados-lista-personas");
                tbody.innerHTML = "";
                if (!data.success || data.data.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4">No hay personas asignadas aún.</td></tr>`;
                    return;
                }
                data.data.forEach(persona => {
                    let row = `<tr>
                        <td>${persona.nombre}</td>
                        <td>${persona.rut}</td>
                        <td>${persona.tipo_persona}</td>
                        <td><!-- Botón eliminar si lo deseas --></td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            })
            .catch(() => {});
    }

    // Si abres el offcanvas/cambias de evento, pon el eventoId en el atributo data-evento-id:
    // $('#personas-content').data('evento-id', idEvento); // Haz esto desde tu script principal al abrir el detalle

    // Carga inicial de personas asignadas (opcional: puedes llamar a esto cuando se cambia de evento)
    // let eventoId = getEventoId();
    // if (eventoId) cargarPersonasAsignadas(eventoId);

    // BONUS: Puedes recargar personas asignadas al cambiar de pestaña si usas Bootstrap tabs:
    $('button[data-bs-target="#personas-content"]').on('shown.bs.tab', function() {
        let eventoId = getEventoId();
        if (eventoId) cargarPersonasAsignadas(eventoId);
    });

});
