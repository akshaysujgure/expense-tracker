import { initTelegram } from "./telegram.js";
import { submitExpense } from "./api.js";
const telegram = initTelegram();
const appState = {
 categories: [
   { name: "Food", subcategories: ["Groceries", "Restaurants", "Other"] },
   { name: "Bills", subcategories: ["Electricity", "Internet", "Other"] },
   { name: "Utilities", subcategories: ["Electricity", "Water", "Other"] },
   { name: "Transport", subcategories: ["Fuel", "Public Transport", "Other"] },
   { name: "Shopping", subcategories: ["Clothing", "Electronics", "Other"] },
   { name: "Other", subcategories: ["Miscellaneous"] }
 ],
 paymentMethods: ["UPI", "Cash", "Credit Card", "Debit Card", "Bank Transfer", "Wallet", "Other"]
};
document.addEventListener("DOMContentLoaded", () => {
 bindNavigation();
 populateCategorySelects();
 populatePaymentMethods();
 bindFormSubmit();
});
function bindNavigation() {
 document.querySelectorAll(".nav-btn").forEach((button) => {
   button.addEventListener("click", () => {
     document.querySelectorAll(".screen").forEach((screen) => screen.classList.remove("active"));
     document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));
     const target = button.dataset.target;
     document.getElementById(target).classList.add("active");
     button.classList.add("active");
   });
 });
}
function populateCategorySelects() {
 const categorySelect = document.getElementById("categorySelect");
 categorySelect.innerHTML = "";
 appState.categories.forEach((category) => {
   const option = document.createElement("option");
   option.value = category.name;
   option.textContent = category.name;
   categorySelect.appendChild(option);
 });
 categorySelect.addEventListener("change", () => {
   renderSubcategories(categorySelect.value);
 });
 renderSubcategories(appState.categories[0].name);
}
function renderSubcategories(categoryName) {
 const category = appState.categories.find((item) => item.name === categoryName);
 const subcategorySelect = document.getElementById("subcategorySelect");
 subcategorySelect.innerHTML = "";
 if (!category) return;
 category.subcategories.forEach((sub) => {
   const option = document.createElement("option");
   option.value = sub;
   option.textContent = sub;
   subcategorySelect.appendChild(option);
 });
}
function populatePaymentMethods() {
 const select = document.getElementById("paymentMethodSelect");
 select.innerHTML = "";
 appState.paymentMethods.forEach((method) => {
   const option = document.createElement("option");
   option.value = method;
   option.textContent = method;
   select.appendChild(option);
 });
}
function bindFormSubmit() {
 document.getElementById("expenseForm").addEventListener("submit", async (event) => {
   event.preventDefault();
   const form = event.target;
   const formData = new FormData(form);
   const payload = {
     amount: Number(formData.get("amount")),
     scope: formData.get("scope"),
     category: formData.get("category"),
     subcategory: formData.get("subcategory"),
     payment_method: formData.get("payment_method"),
     date: formData.get("date"),
     merchant: formData.get("merchant"),
     note: formData.get("note"),
     type: "expense"
   };
   try {
     const result = await submitExpense(payload, telegram.initData);
     alert(result.message || "Saved");
     form.reset();
   } catch (error) {
     alert(error.message || "Unable to save");
   }
 });
}
