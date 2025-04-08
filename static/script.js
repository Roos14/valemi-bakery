let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

// Función para agregar productos al carrito
function agregarAlCarrito(event) {
  const button = event.target;
  const nombre = button.getAttribute("data-nombre");
  const precio = parseFloat(button.getAttribute("data-precio"));

  if (isNaN(precio)) {
    console.error(`El precio de ${nombre} no es válido.`);
    return;
  }

  // Buscar si el producto ya existe en el carrito
  const productoExistente = carrito.find(
    (producto) => producto.nombre === nombre
  );

  if (productoExistente) {
    productoExistente.cantidad += 1; // Aumentar cantidad
    productoExistente.total =
      productoExistente.cantidad * productoExistente.precio; // Actualizar total
  } else {
    // Agregar nuevo producto con cantidad 1
    carrito.push({ nombre, precio, cantidad: 1, total: precio });
  }

  localStorage.setItem("carrito", JSON.stringify(carrito));
  actualizarCarrito();
}

// Función para mostrar los productos en el carrito
function actualizarCarrito() {
  const carritoDiv = document.querySelector("#carrito");
  if (!carritoDiv) return; // Evitar errores si no existe el carrito

  carritoDiv.innerHTML = "";

  if (carrito.length === 0) {
    carritoDiv.innerHTML = "<p>El carrito está vacío.</p>";
    return;
  }

  let totalGeneral = 0;

  carrito.forEach((producto, index) => {
    if (isNaN(producto.precio) || isNaN(producto.total)) {
      console.error(
        `Error con el producto ${producto.nombre}. Precio o total inválido.`
      );
      return;
    }

    totalGeneral += producto.total; // Sumar total general

    const item = document.createElement("div");
    item.innerHTML = `${producto.nombre} x${
      producto.cantidad
    } - RD$ ${producto.total.toFixed(2)}
                      <button onclick="eliminarDelCarrito(${index})">❌</button>`;
    carritoDiv.appendChild(item);
  });

  // Mostrar el total de la compra
  const totalDiv = document.createElement("div");
  totalDiv.innerHTML = `<strong>Total a pagar: RD$ ${totalGeneral.toFixed(
    2
  )}</strong>`;
  carritoDiv.appendChild(totalDiv);
}

// Función para eliminar productos del carrito (decrementar cantidad o eliminar)
function eliminarDelCarrito(index) {
  if (carrito[index].cantidad > 1) {
    carrito[index].cantidad -= 1; // Reducir cantidad
    carrito[index].total = carrito[index].cantidad * carrito[index].precio; // Actualizar total
  } else {
    carrito.splice(index, 1); // Si solo queda 1, eliminar el producto
  }

  localStorage.setItem("carrito", JSON.stringify(carrito));
  actualizarCarrito();
}

// ✅ Nueva función para limpiar completamente el carrito
function limpiarCarrito() {
  carrito = []; // Vaciar el array del carrito
  localStorage.removeItem("carrito"); // Eliminar del almacenamiento local
  actualizarCarrito(); // Refrescar la interfaz
}

// Función para enviar pedido por WhatsApp
function enviarPedido() {
  if (carrito.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }

  let mensaje = "Hola, quiero hacer un pedido:\n";
  let totalGeneral = 0;

  carrito.forEach((producto) => {
    if (isNaN(producto.total)) {
      console.error(`Error con el producto ${producto.nombre}.`);
      return;
    }

    mensaje += `- ${producto.nombre} x${
      producto.cantidad
    } (RD$ ${producto.total.toFixed(2)})\n`;
    totalGeneral += producto.total;
  });

  mensaje += `\nTotal a pagar: RD$ ${totalGeneral.toFixed(2)}`;

  window.open(
    `https://wa.me/18096142896?text=${encodeURIComponent(mensaje)}`,
    "_blank"
  );
}

// Agregar eventos a los botones de "Agregar al carrito"
document.querySelectorAll(".agregar-carrito").forEach((button) => {
  button.addEventListener("click", agregarAlCarrito);
});

// Verificar si el botón de "Finalizar Pedido" existe antes de asignarle evento
const botonFinalizar = document.querySelector("#finalizar-pedido");
if (botonFinalizar) {
  botonFinalizar.addEventListener("click", enviarPedido);
}

// ✅ Evento para el botón de "Limpiar Carrito"
const botonLimpiar = document.querySelector("#limpiar-carrito");
if (botonLimpiar) {
  botonLimpiar.addEventListener("click", limpiarCarrito);
}

// Actualizar el carrito al cargar la página
document.addEventListener("DOMContentLoaded", actualizarCarrito);

// Función para abrir/cerrar el menú en móviles
document.addEventListener("DOMContentLoaded", function () {
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector("nav");

  menuToggle.addEventListener("click", function () {
    nav.classList.toggle("active");
  });
});
