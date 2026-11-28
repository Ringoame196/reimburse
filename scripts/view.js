'use strict';

const items = document.getElementById('items');
const totalAmountEl = document.getElementById('total-amount');
const days = ["日", "月", "火", "水", "木", "金", "土"];

function formatDateWithDay(dateStr) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr).trim());
  if (!match) return String(dateStr);

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const localDate = new Date(year, month - 1, day);
  if (Number.isNaN(localDate.getTime())) return String(dateStr);

  const dayOfWeek = days[localDate.getDay()];
  return `${dateStr}(${dayOfWeek})`;
}

async function getJsonData() {
  try {
    const res = await fetch('/api/expenses');
    if (!res.ok) {
      throw new Error(`HTTPエラー: ${res.status}`);
    }
    const data = await res.json();
    return Array.isArray(data.expenses) ? data.expenses : [];
  } catch (error) {
    console.error('取得に失敗しました:', error);
    return null;
  }
}

function renderExpenses(expenses) {
  if (!items) return;

  if (expenses === null) {
    items.innerHTML = '<div class="alert alert-danger mb-0">データの読み込みに失敗しました。</div>';
    if (totalAmountEl) totalAmountEl.textContent = '0';
    return;
  }

  if (expenses.length === 0) {
    items.innerHTML = '<div class="alert alert-secondary mb-0">精算データはまだありません。</div>';
    if (totalAmountEl) totalAmountEl.textContent = '0';
    return;
  }

  const wrapper = document.createElement('div');
  wrapper.className = 'table-responsive';

  const table = document.createElement('table');
  table.className = 'table table-hover table-striped align-middle mb-0';

  table.innerHTML = `
    <thead class="table-light">
      <tr>
        <th scope="col" style="width: 70px;">ID</th>
        <th scope="col" style="width: 140px;">日付</th>
        <th scope="col">内容</th>
        <th scope="col" class="text-end" style="width: 150px;">金額</th>
      </tr>
    </thead>
    <tbody></tbody>
  `;

  const tbody = table.querySelector('tbody');
  let total = 0;

  expenses.forEach((item) => {
    const amountNum = Number(item.amount) || 0;
    total += amountNum;

    const tr = document.createElement('tr');

    const idTd = document.createElement('td');
    idTd.className = 'text-muted';
    idTd.textContent = item.id;

    const dateTd = document.createElement('td');
    dateTd.textContent = formatDateWithDay(item.date);

    const contentTd = document.createElement('td');
    contentTd.textContent = item.content;

    const amountTd = document.createElement('td');
    amountTd.className = 'text-end fw-semibold';
    amountTd.textContent = `${amountNum.toLocaleString()}円`;

    tr.append(idTd, dateTd, contentTd, amountTd);
    tbody.appendChild(tr);
  });

  wrapper.appendChild(table);
  items.textContent = '';
  items.appendChild(wrapper);

  if (totalAmountEl) {
    totalAmountEl.textContent = total.toLocaleString();
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const expenses = await getJsonData();
  renderExpenses(expenses);
});