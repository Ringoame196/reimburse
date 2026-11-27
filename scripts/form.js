'use strict';

const content = document.getElementById('content');
const date = document.getElementById('date');
const amount = document.getElementById('amount');
const result = document.getElementById('result');

const submitBtn = document.getElementById('submit-btn');
const clearBtn = document.getElementById('clear-btn');

function showResult(message, type) {
  result.textContent = message;
  result.className = `alert alert-${type} mt-4 mb-0`;
}

submitBtn.addEventListener('click', async () => {
  if (content.value.trim() === '' || date.value === '' || amount.value === '') {
    alert('全て入力してください');
    return;
  }

  try {
    await submit();
    showResult('精算データを登録しました。', 'success');
    clearBtn.click();
  } catch (error) {
    showResult('送信に失敗しました。', 'danger');
  }
});

function submit() {
  const data = {
    content: content.value.trim(),
    date: date.value,
    amount: Number(amount.value),
  };

  return postJson('/api/expenses', data);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTPエラー: ${response.status}`);
  }

  return await response.json();
}

clearBtn.addEventListener('click', () => {
  content.value = '';
  date.value = '';
  amount.value = '';
  result.className = 'alert mt-4 mb-0 d-none';
});