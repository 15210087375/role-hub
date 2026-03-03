import { useState, useEffect } from 'react';

/**
 * 本地开发 mock 数据生成器
 * 根据 appId 返回不同的 mock 数据
 */
function getMockData(appId: string, path: string): any {
  console.log(`[Dev Mode] 使用 mock 数据: ${appId}${path}`);

  // 根据 appId 返回不同的 mock 数据
  if (appId === 'todo-app') {
    return [
      { id: '1', title: 'Mock Todo 1 - 完成个人主页开发', completed: false },
      { id: '2', title: 'Mock Todo 2 - 测试部署流程', completed: true },
      { id: '3', title: 'Mock Todo 3 - 编写文档', completed: false }
    ];
  }

  if (appId === 'leave-app') {
    return [
      {
        id: '1',
        type: '年假',
        startDate: '2024-03-01',
        endDate: '2024-03-03',
        status: 'approved',
        days: 3
      },
      {
        id: '2',
        type: '病假',
        startDate: '2024-02-15',
        endDate: '2024-02-15',
        status: 'pending',
        days: 1
      }
    ];
  }

  // HR 系统 - 完整的员工档案 mock 数据
  if (appId === 'hr-system' && path === '/employees/me') {
    return {
      success: true,
      message: '获取个人信息成功',
      data: {
        _id: 'mock-employee-id-123',
        __v: 0,

        // 基本信息
        employeeId: 'E001',
        name: '张三',
        gender: '男',
        age: 28,
        birthDate: '1995-06-15',
        education: '本科',
        school: '北京大学',

        // 组织信息
        company: 'Habby',
        board: '技术中心',
        department: '研发部',
        departmentId: 'dept-dev-001',
        position: '高级软件工程师',

        // 工作状态
        status: 'active',
        joinDate: '2023-01-15',
        serviceType: '全职',
        isProbation: false,
        probationEndDate: null,

        // 联系方式
        workEmail: 'zhangsan@habby.com',
        phone: '13812345678',
        homeAddress: '北京市朝阳区望京街道xxx小区xx号楼xx单元xxx室',
        currentAddress: '北京市朝阳区望京街道xxx小区xx号楼xx单元xxx室',
        registeredAddress: '北京市海淀区xxx街道xxx号',

        // 紧急联系人
        emergencyContact: '李四',
        emergencyPhone: '13987654321',
        emergencyContactPhone: '13987654321',

        // 敏感信息
        idType: '身份证',
        idNumber: '110101199506151234',
        bankName: '招商银行',
        bankAccount: '6225881234567890',

        // 元数据
        createdAt: '2023-01-10T08:00:00.000Z',
        updatedAt: '2024-12-15T10:30:00.000Z',
        updatedBy: 'admin'
      }
    };
  }

  // 默认返回空数组
  return [];
}

export function useApi<T = any>(appId: string, path: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refetch = () => {
    setLoading(true);

    // 🔧 本地开发模式：使用 mock 数据
    if (import.meta.env.DEV) {
      // 模拟网络延迟
      setTimeout(() => {
        const mockData = getMockData(appId, path);
        setData(mockData as T);
        setLoading(false);
      }, 300);
      return;
    }

    // 🌐 生产模式：调用真实 API
    fetch(`/api/${appId}${path}`, {
      credentials: 'include',  // 关键: 携带 cookie
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refetch();
  }, [appId, path]);

  return { data, loading, error, refetch };
}
