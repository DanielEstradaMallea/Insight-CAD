document.addEventListener('DOMContentLoaded', function () {
    // Script para cargar subtipos dinámicamente
    const tipoSelect = document.getElementById('id_id_tipo');
    const subtipoSelect = document.getElementById('id_id_subtipo');

    if (tipoSelect && subtipoSelect) {
        console.log("Campos tipo y subtipo encontrados"); // Depuración

        tipoSelect.addEventListener('change', function () {
            const tipoId = this.value;
            console.log("Tipo seleccionado:", tipoId); // Depuración
            loadSubtipos(tipoId);
        });

        // Cargar subtipos iniciales si hay un tipo seleccionado
        const initialTipoId = tipoSelect.value;
        if (initialTipoId) {
            console.log("Cargando subtipos iniciales para tipo:", initialTipoId); // Depuración
            loadSubtipos(initialTipoId);
        }

        function loadSubtipos(tipoId) {
            if (!tipoId) {
                console.log("No se seleccionó ningún tipo"); // Depuración
                subtipoSelect.innerHTML = '<option value="">Seleccione un tipo primero</option>';
                return;
            }

            console.log("Cargando subtipos para tipo:", tipoId); // Depuración

            fetch(`/api/subtipos/?tipo_id=${tipoId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Error en la solicitud");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Datos recibidos:", data); // Depuración
                    subtipoSelect.innerHTML = '';
                    if (data.length === 0) {
                        subtipoSelect.innerHTML = '<option value="">No hay subtipos disponibles</option>';
                        return;
                    }
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = 'Seleccione un subtipo';
                    subtipoSelect.appendChild(defaultOption);

                    data.forEach(subtipo => {
                        const option = document.createElement('option');
                        option.value = subtipo.id_subtipo;
                        option.textContent = subtipo.nombre;
                        subtipoSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    subtipoSelect.innerHTML = '<option value="">Error al cargar subtipos</option>';
                });
        }
    } else {
        console.error("No se encontraron los campos tipo o subtipo"); // Depuración
    }
});