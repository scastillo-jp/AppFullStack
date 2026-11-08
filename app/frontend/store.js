(() => {
	const API_BASE_URL = "http://localhost:8000";
	const tokenKey = "access_token";

	async function apiFetch(path, options = {}) {
		const headers = new Headers(options.headers || {});
		const token = localStorage.getItem(tokenKey);
		if (token) {
			headers.set("Authorization", `Bearer ${token}`);
		}
		const response = await fetch(`${API_BASE_URL}${path}`, {
			...options,
			headers
		});
		if (response.status === 401 && location.pathname.endsWith(".html")) {
			localStorage.removeItem(tokenKey);
			location.replace("acceso.html");
		}
		return response;
	}

	async function request(path, options) {
		const response = await apiFetch(path, options);
		if (response.status === 204) {
			return null;
		}
		const data = await response.json().catch(() => null);
		if (!response.ok) {
			throw new Error(data?.detail || "No se pudo completar la solicitud.");
		}
		return data;
	}

	async function requireAuth() {
		if (!localStorage.getItem(tokenKey)) {
			location.replace("acceso.html");
			return null;
		}
		try {
			const response = await apiFetch("/auth/me");
			if (response.status === 401) return null;
			const data = await response.json();
			if (!response.ok) throw new Error(data?.detail || "No se pudo validar la sesión.");
			const user = data;
			const loginLink = document.querySelector("#login-link");
			const logoutButton = document.querySelector("#logout-button");
			const userName = document.querySelector(".usuario-autorizado p");
			const authorizedUser = document.querySelector(".usuario-autorizado");
			if (loginLink) loginLink.hidden = true;
			if (logoutButton) logoutButton.hidden = false;
			if (userName) userName.textContent = user.full_name || user.email;
			if (authorizedUser) authorizedUser.hidden = false;
			return user;
		} catch {
			let message = document.querySelector("#auth-mensaje");
			if (!message) {
				message = document.createElement("p");
				message.id = "auth-mensaje";
				message.setAttribute("role", "alert");
				document.querySelector("main")?.prepend(message);
			}
			message.textContent = "No se pudo conectar con el servidor. Inténtalo de nuevo.";
			return null;
		}
	}

	function formatPrice(value) {
		return `$${Number(value).toFixed(2)}`;
	}

	function imageUrl(path) {
		if (!path) return "../assets/logos/logo.png";
		const normalized = String(path).replaceAll("\\", "/");
		if (!normalized.startsWith("assets/") || normalized.includes("..")) {
			return "../assets/logos/logo.png";
		}
		return `../${normalized}`;
	}

	function showMessage(element, message, isError = true) {
		if (!element) return;
		element.textContent = message;
		element.hidden = !message;
		element.classList.toggle("mensaje-error", isError);
	}

	function renderProductCards(container, products) {
		container.replaceChildren();
		if (!products.length) {
			const empty = document.createElement("p");
			empty.className = "carrito-vacio";
			empty.textContent = "No hay productos disponibles.";
			container.append(empty);
			return;
		}

		for (const product of products) {
			const card = document.createElement("article");
			card.className = "item-card";
			const image = document.createElement("img");
			image.src = imageUrl(product.image_path);
			image.alt = product.name;
			const info = document.createElement("div");
			info.className = "item-card-info";
			const name = document.createElement("h3");
			name.textContent = product.name;
			const price = document.createElement("p");
			price.textContent = `Precio: ${formatPrice(product.price)}`;
			const stock = document.createElement("p");
			stock.textContent = `Stock: ${product.stock}`;
			const description = document.createElement("p");
			description.className = "descripcion-producto-recortada";
			description.textContent = product.description || "";
			const link = document.createElement("a");
			link.href = `detalle-item.html?id=${encodeURIComponent(product.id)}`;
			const button = document.createElement("button");
			button.type = "button";
			button.className = "btn-tipo-4 btn-size-full-width mt-5";
			button.textContent = "Ver producto";
			link.append(button);
			info.append(name, price, stock, description, link);
			card.append(image, info);
			container.append(card);
		}
	}

	function renderCategories(container, categories) {
		container.replaceChildren();
		for (const category of categories) {
			const link = document.createElement("a");
			link.className = "categoria-card";
			link.href = `catalogo.html?category_id=${encodeURIComponent(category.id)}`;
			const name = document.createElement("p");
			name.textContent = category.name;
			link.append(name);
			container.append(link);
		}
		if (!categories.length) {
			const empty = document.createElement("p");
			empty.textContent = "Aún no hay categorías disponibles.";
			container.append(empty);
		}
	}

	function logout() {
		localStorage.removeItem(tokenKey);
		location.replace("acceso.html");
	}

	document.querySelector("#logout-button")?.addEventListener("click", logout);

	window.Store = {
		API_BASE_URL,
		apiFetch,
		formatPrice,
		imageUrl,
		renderCategories,
		renderProductCards,
		request,
		requireAuth,
		showMessage,
		tokenKey
	};
})();
