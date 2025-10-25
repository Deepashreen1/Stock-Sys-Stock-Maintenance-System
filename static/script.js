// Show confirmation before deleting a product
function confirmDelete(productName) {
  return confirm("Are you sure you want to delete " + productName + "?");
}

// Auto-hide Bootstrap alerts after 3 seconds
setTimeout(function () {
  let alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    alert.classList.add("fade");
    setTimeout(() => alert.remove(), 500);
  });
}, 3000);

// Highlight low stock rows in tables (optional visual effect)
document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll("table tbody tr");
  rows.forEach(row => {
    let qtyCell = row.cells[3]; // Assuming quantity is 4th column
    if (qtyCell) {
      let qty = parseInt(qtyCell.textContent);
      if (!isNaN(qty) && qty < 5) {
        row.style.backgroundColor = "#fff3cd"; // light yellow warning
      }
    }
  });
});