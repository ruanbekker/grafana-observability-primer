import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    vus: 5,
    duration: '20s',
};

export default function () {
    const res = http.get('http://app:5000/users/1');
    const params = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

	check(res, {
        'is status 200': (r) => r.status === 200,
        'returns k6@k6.io': (r) => r.body.includes('k6@k6.io'),
    });
    sleep(1);
}
