# React + TypeScript + Vite 脚手架模板

## 创建命令

```bash
npm create vite@latest {project-name}-web -- --template react-ts
cd {project-name}-web
npm install
```

## 核心依赖

```bash
# UI 组件库
npm install antd @ant-design/icons

# 路由
npm install react-router-dom

# 状态管理
npm install zustand

# HTTP 请求
npm install axios

# 工具
npm install dayjs

# 开发依赖
npm install -D @types/node eslint prettier eslint-config-prettier
```

## 项目结构

```
src/
├── main.tsx                          # 应用入口
├── App.tsx                           # 根组件（路由出口）
├── vite-env.d.ts
├── routes/
│   └── index.tsx                     # 路由配置
├── pages/
│   ├── Login/
│   │   └── index.tsx                 # 登录页
│   ├── Dashboard/
│   │   └── index.tsx                 # 首页仪表盘
│   └── NotFound/
│       └── index.tsx                 # 404 页面
├── components/
│   └── Layout/
│       ├── index.tsx                 # 主布局（侧边栏 + 顶栏）
│       ├── Sidebar.tsx               # 侧边栏导航
│       └── Header.tsx                # 顶部导航栏
├── hooks/
│   └── useAuth.ts                    # 认证 Hook
├── services/
│   ├── api.ts                        # Axios 实例 + 拦截器
│   └── auth.ts                       # 认证相关 API
├── stores/
│   └── useAuthStore.ts               # 认证状态 (zustand)
├── types/
│   ├── api.d.ts                      # API 响应类型
│   └── auth.d.ts                     # 认证相关类型
└── utils/
    └── token.ts                      # Token 存取工具
```

## 关键文件模板

### main.tsx

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>
);
```

### App.tsx

```tsx
import { useRoutes } from 'react-router-dom';
import routes from './routes';

function App() {
  const element = useRoutes(routes);
  return element;
}

export default App;
```

### routes/index.tsx

```tsx
import { lazy, Suspense } from 'react';
import { Navigate, type RouteObject } from 'react-router-dom';
import Layout from '../components/Layout';

const Login = lazy(() => import('../pages/Login'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const NotFound = lazy(() => import('../pages/NotFound'));

const Lazy = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>
);

const routes: RouteObject[] = [
  {
    path: '/login',
    element: <Lazy><Login /></Lazy>,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <Lazy><Dashboard /></Lazy> },
    ],
  },
  { path: '*', element: <Lazy><NotFound /></Lazy> },
];

export default routes;
```

### services/api.ts

```tsx
import axios from 'axios';
import { getToken, removeToken } from '../utils/token';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
});

// 请求拦截器：自动附加 Token
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error.message);
  }
);

export default api;
```

### utils/token.ts

```tsx
const TOKEN_KEY = 'access_token';

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string): void => localStorage.setItem(TOKEN_KEY, token);

export const removeToken = (): void => localStorage.removeItem(TOKEN_KEY);
```

### services/auth.ts

```tsx
import api from './api';

export interface LoginParams {
  username: string;
  password: string;
}

export interface LoginResult {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

export const authService = {
  login: (params: LoginParams): Promise<LoginResult> =>
    api.post('/auth/login', params),

  logout: (): Promise<void> =>
    api.post('/auth/logout'),

  getCurrentUser: () =>
    api.get('/auth/me'),
};
```

### stores/useAuthStore.ts

```tsx
import { create } from 'zustand';
import { getToken, setToken, removeToken } from '../utils/token';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: getToken(),
  isAuthenticated: !!getToken(),
  login: (token, user) => {
    setToken(token);
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    removeToken();
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
```

### pages/Login/index.tsx

```tsx
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/useAuthStore';
import { authService } from '../../services/auth';

export default function Login() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const { token, user } = await authService.login(values);
      login(token, user);
      message.success('登录成功');
      navigate('/dashboard');
    } catch {
      message.error('登录失败，请检查用户名和密码');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card title="系统登录" style={{ width: 400 }}>
        <Form onFinish={onFinish} autoComplete="off">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>登录</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
```

### pages/Dashboard/index.tsx

```tsx
import { Card, Col, Row, Statistic } from 'antd';
import { TeamOutlined, ProjectOutlined, CheckCircleOutlined } from '@ant-design/icons';

export default function Dashboard() {
  return (
    <div>
      <h2>仪表盘</h2>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="用户数" value={0} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="项目数" value={0} prefix={<ProjectOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="已完成" value={0} prefix={<CheckCircleOutlined />} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
```

### pages/NotFound/index.tsx

```tsx
import { Button, Result } from 'antd';
import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <Result
      status="404"
      title="404"
      subTitle="抱歉，您访问的页面不存在"
      extra={
        <Button type="primary" onClick={() => navigate('/')}>
          返回首页
        </Button>
      }
    />
  );
}
```

### components/Layout/index.tsx

```tsx
import { Outlet, useNavigate } from 'react-router-dom';
import { Layout as AntLayout, Menu, Avatar, Dropdown, theme } from 'antd';
import { DashboardOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../stores/useAuthStore';

const { Header, Sider, Content } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider collapsible>
        <div style={{ height: 32, margin: 16, color: '#fff', textAlign: 'center', fontSize: 18 }}>
          Logo
        </div>
        <Menu
          theme="dark"
          mode="inline"
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <AntLayout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Dropdown menu={{
            items: [
              { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', onClick: () => { logout(); navigate('/login'); } },
            ]
          }}>
            <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <div style={{ padding: 24, background: colorBgContainer, borderRadius: borderRadiusLG, minHeight: 360 }}>
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
}
```

### vite.config.ts

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
```

### tsconfig.json 补充

```json
{
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### .env.example

```
VITE_API_BASE_URL=/api
```

### Dockerfile（Nginx 托管）

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### .dockerignore

```
node_modules/
dist/
.git/
.gitignore
*.log
.env*
README.md
COPILOT_README.md
```

### nginx.conf

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### docker-compose.yml（项目根目录 · .NET 后端版）

```yaml
services:
  backend:
    build:
      context: ./{project-name}
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Server=db;Database={ProjectName};User=sa;Password=${DB_PASSWORD:-YourStrong!Pass123};TrustServerCertificate=true
      - Jwt__Secret=${JWT_SECRET:-dev-only-secret-change-in-production-32chars}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./{project-name}-web
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=${DB_PASSWORD:-YourStrong!Pass123}
    ports:
      - "1433:1433"
    volumes:
      - db-data:/var/opt/mssql
    healthcheck:
      test: /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db-data:
```

### .gitignore

```
node_modules/
dist/
.env.local
.env.*.local
*.log
.DS_Store
```
