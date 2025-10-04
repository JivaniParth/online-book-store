// Complete API Service for BookHaven Frontend
const API_BASE_URL = "http://localhost:5000/api";

class ApiService {
  constructor() {
    this.token = localStorage.getItem("access_token");
  }

  getHeaders(includeAuth = true) {
    const headers = {
      "Content-Type": "application/json",
    };

    if (includeAuth && this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async handleResponse(response) {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    return data;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }

  getToken() {
    return this.token;
  }

  // ==================== AUTHENTICATION ====================

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: this.getHeaders(false),
      body: JSON.stringify({ email, password }),
    });
    const data = await this.handleResponse(response);
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: this.getHeaders(false),
      body: JSON.stringify(userData),
    });
    const data = await this.handleResponse(response);
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async getProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async updateProfile(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });
    return await this.handleResponse(response);
  }

  async verifyToken() {
    const response = await fetch(`${API_BASE_URL}/auth/verify-token`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== BOOKS ====================

  async getBooks(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/books${queryString ? `?${queryString}` : ""}`;
    const response = await fetch(url, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getBook(bookId) {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getCategories() {
    const response = await fetch(`${API_BASE_URL}/books/categories`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getAuthors() {
    const response = await fetch(`${API_BASE_URL}/books/authors`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getPublishers() {
    const response = await fetch(`${API_BASE_URL}/books/publishers`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getFilters() {
    const response = await fetch(`${API_BASE_URL}/books/filters`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  // ==================== CART ====================

  async getCart() {
    const response = await fetch(`${API_BASE_URL}/cart`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async addToCart(bookId, quantity = 1) {
    const response = await fetch(`${API_BASE_URL}/cart/add`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ book_id: bookId, quantity }),
    });
    return await this.handleResponse(response);
  }

  async updateCartItem(bookId, quantity) {
    const response = await fetch(`${API_BASE_URL}/cart/update`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify({ book_id: bookId, quantity }),
    });
    return await this.handleResponse(response);
  }

  async removeFromCart(bookId) {
    const response = await fetch(`${API_BASE_URL}/cart/remove/${bookId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async clearCart() {
    const response = await fetch(`${API_BASE_URL}/cart/clear`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== ORDERS ====================

  async getOrders(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/orders${queryString ? `?${queryString}` : ""}`;
    const response = await fetch(url, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async getOrder(orderId) {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async createOrder(orderData) {
    const response = await fetch(`${API_BASE_URL}/orders/create`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(orderData),
    });
    return await this.handleResponse(response);
  }

  async cancelOrder(orderId) {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/cancel`, {
      method: "PUT",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async getOrderStats() {
    const response = await fetch(`${API_BASE_URL}/orders/stats`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== REVIEWS ====================

  async getBookReviews(bookId) {
    const response = await fetch(`${API_BASE_URL}/reviews/book/${bookId}`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  async getUserReviews() {
    const response = await fetch(`${API_BASE_URL}/reviews/user`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  async createReview(reviewData) {
    const response = await fetch(`${API_BASE_URL}/reviews`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(reviewData),
    });
    return await this.handleResponse(response);
  }

  async updateReview(reviewId, reviewData) {
    const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(reviewData),
    });
    return await this.handleResponse(response);
  }

  async deleteReview(reviewId) {
    const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== ADMIN (if user is admin) ====================

  async adminGetStats() {
    const response = await fetch(`${API_BASE_URL}/admin/stats`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return await this.handleResponse(response);
  }

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      headers: this.getHeaders(false),
    });
    return await this.handleResponse(response);
  }

  logout() {
    this.setToken(null);
  }

  isAuthenticated() {
    return !!this.token;
  }
}

export default new ApiService();
