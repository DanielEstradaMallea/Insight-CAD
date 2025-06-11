// Helper global para CSRF desde cookie
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

class AlertHandler {
    static init() {
        // Manejar clic en botones de alerta
        $(document).off('click', '.btn-alerta').on('click', '.btn-alerta', (e) => {
            const boton = $(e.currentTarget);
            const eventoId = boton.data('evento-id');
            const estadoActual = boton.data('estado-alerta'); // "SI" o "NO"

            if (!eventoId || typeof estadoActual === "undefined") {
                console.error('Faltan datos para cambiar el estado de la alerta');
                return;
            }
            this.mostrarModalConfirmacion(eventoId, estadoActual);
        });

        // Confirmar cambio en el modal
        $('#confirmarCambio').off('click').on('click', () => {
            this.cambiarEstadoAlerta();
        });

        // Limpiar modal al cerrar
        $('#confirmarAlertaModal').on('hidden.bs.modal', function () {
            $(this).removeData('evento-id').removeData('estado-actual');
            $('#mensajeConfirmacion').text('¿Desea cambiar el estado de la alerta?');
            $('#confirmarCambio').prop('disabled', false).html('Sí');
        });
    }

    static mostrarModalConfirmacion(eventoId, estadoActual) {
        const modal = new bootstrap.Modal('#confirmarAlertaModal');
        const mensaje = estadoActual === 'SI' 
            ? '¿Desea apagar la alerta?' 
            : '¿Desea encender la alerta?';
        $('#mensajeConfirmacion').text(mensaje);
        $('#confirmarAlertaModal').data('evento-id', eventoId);
        $('#confirmarAlertaModal').data('estado-actual', estadoActual);
        modal.show();
    }

    static cambiarEstadoAlerta() {
        const modal = $('#confirmarAlertaModal');
        const eventoId = modal.data('evento-id');
        const estadoActual = modal.data('estado-actual');
        const nuevoEstado = estadoActual === 'SI' ? 'NO' : 'SI';

        if (!eventoId) {
            console.error('No se encontró el ID del evento');
            return;
        }

        // Spinner en botón
        const confirmarBtn = $('#confirmarCambio');
        confirmarBtn.prop('disabled', true)
            .html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cambiando...');

        // CSRF desde cookie
        const csrfToken = getCookie('csrftoken');

        $.ajax({
            url: `/cambiar-estado-alerta/${eventoId}/`,
            method: 'POST',
            data: {
                nuevo_estado: nuevoEstado
            },
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: (data) => {
                if (data.success) {
                    this.actualizarInterfaz(eventoId, nuevoEstado);
                    bootstrap.Modal.getInstance(modal[0]).hide();
                } else {
                    alert('Error al cambiar el estado de la alerta: ' + (data.error || ''));
                }
            },
            error: () => {
                alert('Error en la solicitud. Intente nuevamente.');
            },
            complete: () => {
                confirmarBtn.prop('disabled', false).html('Sí');
            }
        });
    }

    static actualizarInterfaz(eventoId, nuevoEstado) {
        const botonAlerta = $(`.btn-alerta[data-evento-id="${eventoId}"]`);
        // Actualizar visual según el estado
        if (nuevoEstado === 'SI') {
            botonAlerta.html('<i class="fas fa-bell fa-shake"></i> Activa');
            botonAlerta.removeClass('btn-secondary').addClass('btn-danger');
        } else {
            botonAlerta.html('<i class="fas fa-bell-slash"></i> No');
            botonAlerta.removeClass('btn-danger').addClass('btn-secondary');
        }
        botonAlerta.data('estado-alerta', nuevoEstado);
    }
}

$(document).ready(function() {
    AlertHandler.init();
});
