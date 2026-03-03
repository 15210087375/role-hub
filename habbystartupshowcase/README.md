# 个人主页模板

这是 habby 个人主页的项目模板。

## 页面类型说明

此模板默认创建的是**私人主页**，展示当前登录用户的个人信息。

### 两种页面类型

**📢 公开主页 (Public Homepage)**
- **路径：** `/`
- **访问权限：** 所有登录用户都可以访问
- **展示内容：** 创建者的公开信息（技能、经历、联系方式等）
- **特点：** 静态内容，展示的是创建者的信息，不会因访问者不同而变化
- **场景：** 个人简介、技能展示、工作经历、公开项目
- **实现：** 静态数据，不调用 API

**🔒 私人页面 (Private Page)**
- **路径：** `/private`
- **访问权限：** ⚠️ **仅限创建者本人访问**（通过 `src/config.ts` 中的 `OWNER_EMAIL` 验证）
- **展示内容：** 创建者的私人 HR 信息（包括敏感数据）
- **特点：** 需要 SSO 登录 + 创建者身份验证
- **场景：** 个人 HR 档案、敏感信息查看
- **实现：** 调用 `https://apps.habby.com/api/hr-system/employees/me` 接口

**🔐 访问控制说明**：
- 公开主页：任何登录用户都能访问，看到的是创建者的公开信息
- 私人页面：只有创建者本人（email 匹配）才能访问，其他用户会看到"无权访问"

## 快速开始

### 🔴 步骤 0：必须修改创建者邮箱（强制要求）

**这不是可选步骤，这是必须遵守的安全规则！**

编辑 `src/config.ts`，将 `OWNER_EMAIL` 修改为**你自己的 Habby 邮箱**：

```typescript
export const config = {
  OWNER_EMAIL: 'yourname@habby.com',  // 👈👈👈 必须改为你自己的邮箱！
  // ...
};
```

**为什么必须修改？**
- 🔐 这个邮箱用于保护你的私人页面（`/private`）
- 🔐 私人页面展示你的敏感 HR 信息（身份证、银行卡、手机号等）
- 🔐 只有邮箱匹配的登录用户才能访问私人页面
- 🔐 其他用户访问会看到"无权访问"提示

**如果不修改会怎样？**
- ❌ 默认值是 `developer@habby.com`
- ❌ 你自己将无法访问自己的私人页面
- ❌ 只有 `developer@habby.com` 这个邮箱的用户能访问

**填写规则：**
1. ✅ 必须填写你在 Habby 系统中的工作邮箱
2. ✅ 必须与你登录 `apps.habby.com` 时使用的邮箱一致
3. ✅ 区分大小写，请确保完全一致

---

### 1. 修改配置

**b. 配置部署路径**

编辑 `vite.config.ts`，修改 `base` 路径：

```typescript
base: '/personalpage/你的仓库名/',  // 改为你的仓库名，如 alice-homepage
```

### 2. 安装依赖

```bash
npm install
```

### 3. 本地开发

```bash
npm run dev
```

访问 http://localhost:5173

**本地开发说明：**

- ✅ **自动使用 mock 数据** - 本地开发时自动使用 mock SSO 登录状态和 mock API 数据
- ✅ **无需真实登录** - 不需要先登录 apps.habby.com
- ✅ **可以验证 UI 效果** - 测试页面布局、样式、组件交互
- ⚠️ **无法测试真实功能** - 真实的 SSO 认证和 API 调用需要在部署后测试

**Mock 数据位置：**
- 用户信息：`src/hooks/useCurrentUser.ts` - Mock Developer (developer@habby.com)
- API 数据：`src/hooks/useApi.ts` - 根据 appId 返回不同的 mock 数据

**自定义 Mock 数据：**

如果需要修改 mock 数据，编辑 `src/hooks/useApi.ts` 中的 `getMockData` 函数：

```typescript
function getMockData(appId: string, path: string): any {
  if (appId === 'your-app') {
    return [
      // 你的 mock 数据
    ];
  }
}
```

### 4. 部署

```bash
git add .
git commit -m "Initial commit"
git push
```

GitHub Actions 会自动构建和部署，约 2 分钟后访问：

```
https://apps.habby.com/personalpage/你的仓库名/
```

## API 使用

### 获取当前用户

```typescript
import { useCurrentUser } from './hooks/useCurrentUser';

function MyComponent() {
  const { user, loading, error } = useCurrentUser();

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;

  return <div>你好, {user.name}！</div>;
}
```

### 调用业务 API

```typescript
import { useApi } from './hooks/useApi';

function TodoList() {
  const { data: todos, loading, error, refetch } = useApi('todo-app', '/api/my-todos');

  return (
    <div>
      {todos?.map(todo => (
        <div key={todo.id}>{todo.title}</div>
      ))}
    </div>
  );
}
```

支持的 appId:
- `todo-app` - 待办事项
- `leave-app` - 请假管理
- `hr-app` - 人力资源
- 其他已部署的应用

### 📚 查找更多可集成的 API

想要集成其他业务 API 到你的私人页面？

**访问 API 文档中心：https://apps.habby.com/habby-app-hub/**

点击"API 文档"页面，可以查看所有已部署应用的 API 接口文档：
- 请假管理 API
- 报销管理 API
- HR 系统 API
- 其他平台应用 API

**集成步骤：**
1. 在 API 文档中心找到你需要的接口
2. 参考 `src/hooks/useHrInfo.ts` 创建对应的 hook
3. 在私人页面中使用新创建的 hook

## UI 定制

💡 **模板只是起点，你可以按自己喜欢的风格定制！**

修改 CSS 文件（`src/App.css`、`src/pages/*.css`）或安装 UI 库（Ant Design、Tailwind CSS）自由定制样式。

## 常见问题

### Q: 如何调试 API 调用？

A: 本地开发时，Vite 会自动代理 `/api/*` 请求到生产环境。打开浏览器开发者工具 → Network 查看请求。

### Q: 如何添加新的依赖？

A: 直接使用 npm 安装：

```bash
npm install antd  # 或其他任何包
```

### Q: 如何更新部署？

A: 修改代码后提交推送即可：

```bash
git add .
git commit -m "Update homepage"
git push
```

### Q: 如何查看部署状态？

A: 访问 GitHub 仓库的 Actions 标签页查看部署日志。

## 技术栈

- **构建工具**: Vite 5
- **框架**: React 18
- **语言**: TypeScript 5
- **部署**: GitHub Actions + rsync
