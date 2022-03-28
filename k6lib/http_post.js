import http from 'k6/http';

export default function () {
  const url = 'http://app:5000/users';
  const payload = JSON.stringify({
    username: 'k6',
    email: 'k6@k6.io',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  http.post(url, payload, params);
}

