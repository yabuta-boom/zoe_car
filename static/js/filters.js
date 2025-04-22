class VehicleFilters {
    constructor() {
      this.form = document.getElementById('inventory-filter');
      this.vehicleCards = document.querySelectorAll('.vehicle-card');
      this.noResults = document.querySelector('.no-results');
      
      if (this.form) {
        this.initEvents();
        this.applyInitialFilters();
      }
    }
  
    initEvents() {
      this.form.addEventListener('change', this.handleFilterChange.bind(this));
      this.form.addEventListener('submit', this.handleFormSubmit.bind(this));
    }
  
    applyInitialFilters() {
      const params = new URLSearchParams(window.location.search);
      if (params.toString()) {
        this.filterVehicles();
      }
    }
  
    handleFilterChange() {
      this.updateURL();
      this.filterVehicles();
    }
  
    handleFormSubmit(e) {
      e.preventDefault();
      this.filterVehicles();
    }
  
    filterVehicles() {
      const formData = new FormData(this.form);
      const filters = Object.fromEntries(formData.entries());
      let visibleCount = 0;
  
      this.vehicleCards.forEach(card => {
        const matches = this.checkFilters(card, filters);
        card.style.display = matches ? 'block' : 'none';
        if (matches) visibleCount++;
      });
  
      this.toggleNoResults(visibleCount === 0);
    }
  
    checkFilters(card, filters) {
      const cardData = {
        make: card.dataset.make,
        model: card.dataset.model,
        year: parseInt(card.dataset.year),
        price: parseFloat(card.dataset.price),
        type: card.dataset.type
      };
  
      return Object.entries(filters).every(([key, value]) => {
        if (!value) return true;
        
        switch(key) {
          case 'min_year':
            return cardData.year >= parseInt(value);
          case 'max_price':
            return cardData.price <= parseFloat(value);
          default:
            return cardData[key] === value;
        }
      });
    }
  
    toggleNoResults(show) {
      if (this.noResults) {
        this.noResults.style.display = show ? 'block' : 'none';
      }
    }
  
    updateURL() {
      const formData = new FormData(this.form);
      const params = new URLSearchParams();
      
      for (const [key, value] of formData.entries()) {
        if (value) params.set(key, value);
      }
  
      history.replaceState(null, '', `?${params.toString()}`);
    }
  }
  
  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    new VehicleFilters();
  });