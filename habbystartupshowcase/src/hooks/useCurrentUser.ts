import { useState, useEffect } from 'react';

export interface User {
  sub: string;
  name: string;
  email: string;
  roles: string[];
}

export function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // 🔧 本地开发模式：使用 mock 数据
    if (import.meta.env.DEV) {
      console.log('[Dev Mode] 使用 mock 用户数据');

      // 模拟网络延迟
      setTimeout(() => {
        setUser({
          sub: 'mock-user-id-12345',
          name: 'Mock Developer',
          email: 'developer@habby.com',
          roles: ['user', 'developer']
        });
        setLoading(false);
      }, 500);

      return;
    }

    // 🌐 生产模式：使用真实 SSO 认证
    fetch('/api/habby-app-hub/me/profile', {
      credentials: 'include',  // 关键: 携带 cookie
    })
      .then((res) => {
        // 🔐 401 自动跳转登录
        if (res.status === 401) {
          // 获取当前应用的 base 路径作为 returnUrl
          const basePath = import.meta.env.BASE_URL;
          const returnUrl = encodeURIComponent(basePath);
          const loginUrl = `https://apps.habby.com/api/habby-app-hub/auth/login?returnUrl=${returnUrl}`;

          console.log('[Auth] 未登录，跳转到登录页:', loginUrl);
          window.location.href = loginUrl;
          return; // 阻止后续处理
        }

        if (!res.ok) throw new Error('Not authenticated');
        return res.json();
      })
      .then((response) => {
        if (!response) return; // 401 跳转时会返回 undefined

        if (response.success && response.data) {
          setUser(response.data);
        } else {
          throw new Error('Invalid response format');
        }
      })
      .catch((err) => {
        setError(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return { user, loading, error };
}
