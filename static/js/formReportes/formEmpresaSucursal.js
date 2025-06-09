document.addEventListener('DOMContentLoaded', function () {
    // Script para cargar sucursales dinámicamente
    const empresaSelect = document.getElementById('id_empresa');
    const sucursalSelect = document.getElementById('id_sucursal');

    if (empresaSelect && sucursalSelect) {
        console.log("Campos empresa y sucursal encontrados"); // Depuración

        empresaSelect.addEventListener('change', function () {
            const empresaId = this.value;
            console.log("Empresa seleccionada:", empresaId); // Depuración
            loadSucursales(empresaId);
        });

        // Cargar sucursales iniciales si hay una empresa seleccionada
        const initialEmpresaId = empresaSelect.value;
        if (initialEmpresaId) {
            console.log("Cargando sucursales iniciales para empresa:", initialEmpresaId); // Depuración
            loadSucursales(initialEmpresaId);
        }

        function loadSucursales(empresaId) {
            if (!empresaId) {
                console.log("No se seleccionó ninguna empresa"); // Depuración
                sucursalSelect.innerHTML = '<option value="">Seleccione una empresa primero</option>';
                return;
            }

            console.log("Cargando sucursales para empresa:", empresaId); // Depuración

            fetch(`/cargar-sucursales/?empresa_id=${empresaId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Error en la solicitud");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Datos recibidos:", data); // Depuración
                    sucursalSelect.innerHTML = '';
                    if (data.length === 0) {
                        sucursalSelect.innerHTML = '<option value="">No hay sucursales disponibles</option>';
                        return;
                    }
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = 'Seleccione una sucursal';
                    sucursalSelect.appendChild(defaultOption);

                    data.forEach(sucursal => {
                        const option = document.createElement('option');
                        option.value = sucursal.id_sucursal;
                        option.textContent = sucursal.nombre;
                        sucursalSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    sucursalSelect.innerHTML = '<option value="">Error al cargar sucursales</option>';
                });
        }
    } else {
        console.error("No se encontraron los campos empresa o sucursal"); // Depuración
    }
});