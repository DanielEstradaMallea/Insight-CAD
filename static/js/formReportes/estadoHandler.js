function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class EstadoHandler {
    static init() {
        // Click en badge para cambiar estado
        $(document).off('click', '.btn-estado').on('click', '.btn-estado', (e) => {
            const eventoId = $(e.currentTarget).data('evento-id');
            const estadoActual = $(e.currentTarget).data('estado-actual');
            if (!eventoId || !estadoActual) {
                console.error('Faltan datos para cambiar el estado del evento');
                return;
            }
            const modal = $('#cambiarEstadoModal');
            modal.data('evento-id', eventoId);
            modal.data('estado-actual', estadoActual);
            this.cargarEstados(eventoId, estadoActual);
            this.cargarHistorialEstados(eventoId);

            // Mostrar modal
            const bsModal = new bootstrap.Modal(modal[0]);
            bsModal.show();
        });

        // Submit formulario de cambio
        $('#formCambiarEstado').off('submit').on('submit', (e) => {
            e.preventDefault();
            this.cambiarEstado();
        });

        // Reinicio del modal al cerrar
        $('#cambiarEstadoModal').on('hidden.bs.modal', function () {
            $(this).removeData('evento-id').removeData('estado-actual');
            $('#nuevoEstado').empty();
            $('#historialEstados').empty();
            $('#formCambiarEstado')[0].reset();
        });
    }

    static cargarEstados(eventoId, estadoActual) {
        $.ajax({
            url: '/obtener-estados/',
            method: 'GET',
            success: (data) => {
                this.mostrarEstados(data.estados, estadoActual);
            },
            error: () => {
                alert('Error al cargar los estados disponibles.');
            }
        });
    }

    static cargarHistorialEstados(eventoId) {
        $('#spinnerHistorialEstado').show();
        $('#historialEstados').hide();
        $.ajax({
            url: `/obtener-historial-estados/${eventoId}/`,
            method: 'GET',
            success: (data) => {
                this.mostrarHistorialEstados(data.historial);
            },
            error: () => {
                $('#historialEstados').html(`<div class="alert alert-danger">Error al cargar el historial de estados.</div>`);
            },
            complete: () => {
                $('#spinnerHistorialEstado').hide();
                $('#historialEstados').show();
            }
        });
    }

    static mostrarEstados(estados, estadoActual) {
        const select = $('#nuevoEstado');
        select.empty();
        estados.forEach((estado) => {
            const selected = estado.nombre === estadoActual ? 'selected' : '';
            select.append(`<option value="${estado.id_estado}" ${selected}>${estado.nombre}</option>`);
        });
    }

    static mostrarHistorialEstados(historial) {
        const lista = $('#historialEstados');
        lista.empty();
        if (!historial || historial.length === 0) {
            lista.html(`<div class="alert alert-info">No hay cambios de estado registrados.</div>`);
            return;
        }
        historial.forEach((cambio) => {
            const fechaHora = new Date(cambio.fecha_registro).toLocaleString('es-CL');
            const estadoClass = this.getEstadoClass(cambio.id_estado__nombre);
            lista.append(`
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge ${estadoClass}">${cambio.id_estado__nombre}</span>
                        <span class="text-muted">${fechaHora}</span>
                        <span class="text-muted">Usuario: ${cambio.id_usuario}</span>
                    </div>
                </div>
            `);
        });
    }

    static getEstadoClass(estadoNombre) {
        switch (estadoNombre) {
            case 'Activo': return 'bg-success';
            case 'Pendiente': return 'bg-warning text-dark';
            case 'Inactivo': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }

    static cambiarEstado() {
        const modal = $('#cambiarEstadoModal');
        const eventoId = modal.data('evento-id');
        const nuevoEstadoId = $('#nuevoEstado').val();

        if (!eventoId || !nuevoEstadoId) {
            alert('Seleccione un estado válido.');
            return;
        }

        // Spinner en botón
        const guardarBtn = $('#btnGuardarEstado');
        guardarBtn.prop('disabled', true)
            .html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cambiando Estado...');

        const csrfToken = getCookie('csrftoken');
        $.ajax({
            url: `/cambiar-estado-evento/${eventoId}/`,
            method: 'POST',
            data: {
                nuevo_estado_id: nuevoEstadoId
            },
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: (data) => {
                if (data.success) {
                    this.actualizarBadgeEstado(eventoId, data.nuevo_estado);
                    this.cargarHistorialEstados(eventoId);
                    bootstrap.Modal.getInstance(modal[0]).hide();
                } else {
                    alert('Error al cambiar el estado: ' + (data.error || ''));
                }
            },
            error: () => {
                alert('Error en la solicitud. Intente nuevamente.');
            },
            complete: () => {
                guardarBtn.prop('disabled', false).html('Guardar');
            }
        });
    }

    static actualizarBadgeEstado(eventoId, nuevoEstado) {
        const badge = $(`.btn-estado[data-evento-id="${eventoId}"]`);
        badge.text(nuevoEstado.nombre);
        badge.data('estado-actual', nuevoEstado.nombre);
        // Cambiar color de fondo si lo deseas
        badge.removeClass('bg-success bg-warning bg-danger bg-secondary');
        badge.addClass(this.getEstadoClass(nuevoEstado.nombre));
    }
}

$(document).ready(function() {
    EstadoHandler.init();
});
