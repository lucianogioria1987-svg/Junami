
        function abrirModalNuevoMensaje() {
            const modal = document.getElementById('modalNuevoMensaje');
            if(!modal) return;
            const content = document.getElementById('modalNuevoMensajeContent');
            modal.classList.remove('hidden');
            void modal.offsetWidth; // force reflow
            modal.classList.remove('opacity-0');
            content.classList.remove('translate-y-full', 'sm:translate-y-10');
            content.classList.add('translate-y-0');
        }
        function cerrarModalNuevoMensaje() {
            const modal = document.getElementById('modalNuevoMensaje');
            if(!modal) return;
            const content = document.getElementById('modalNuevoMensajeContent');
            modal.classList.add('opacity-0');
            content.classList.remove('translate-y-0');
            content.classList.add('translate-y-full', 'sm:translate-y-10');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    
        // DELEGACION DE EVENTOS GLOBAL
        document.addEventListener('click', function(e) {
            let btnVer = e.target.closest('.btn-ver');
            if(btnVer) {
                let id = btnVer.getAttribute('data-id');
                let emisor = btnVer.getAttribute('data-emisor');
                let fecha = btnVer.getAttribute('data-fecha');
                let asunto = btnVer.getAttribute('data-asunto');
                let leido = btnVer.getAttribute('data-leido') === 'true';
                let tipo = btnVer.getAttribute('data-tipo');
                abrirModalLectura(id, emisor, fecha, asunto, null, leido, tipo);
                return;
            }
            
            let btnArchivar = e.target.closest('.btn-archivar');
            if(btnArchivar) {
                archivarMensaje(btnArchivar.getAttribute('data-id'));
                return;
            }
            
            let btnDesarchivar = e.target.closest('.btn-desarchivar');
            if(btnDesarchivar) {
                desarchivarMensaje(btnDesarchivar.getAttribute('data-id'));
                return;
            }
            
            let btnBorrar = e.target.closest('.btn-borrar');
            if(btnBorrar) {
                borrarMensaje(btnBorrar.getAttribute('data-id'));
                return;
            }
        });

