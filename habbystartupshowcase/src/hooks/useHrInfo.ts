import { useApi } from './useApi';

/**
 * HR 员工完整数据结构
 *
 * 根据 HR 系统 API 文档定义的完整字段
 * 参考：https://apps.habby.com/api/hr-system/employees/me
 */
export interface HrEmployee {
  // MongoDB 字段
  _id: string;
  __v?: number;

  // 基本信息
  employeeId: string;
  name: string;
  gender?: string;
  age?: number;
  birthDate?: string;
  education?: string;
  school?: string;

  // 组织信息
  company?: string;
  board?: string;
  department: string;
  departmentId?: string;
  position: string;

  // 工作状态
  status: 'active' | 'resigned' | string;
  joinDate: string;
  serviceType?: string;
  isProbation?: boolean;
  probationEndDate?: string | null;

  // 联系方式
  workEmail: string;
  phone?: string;
  homeAddress?: string;
  currentAddress?: string;
  registeredAddress?: string;

  // 紧急联系人
  emergencyContact?: string;
  emergencyPhone?: string;
  emergencyContactPhone?: string;

  // 敏感信息
  idType?: string;
  idNumber?: string;
  bankName?: string;
  bankAccount?: string;

  // 元数据
  createdAt?: string;
  updatedAt?: string;
  updatedBy?: string;
}

/**
 * HR API 响应格式
 */
export interface HrApiResponse {
  success: boolean;
  message: string;
  data?: HrEmployee;
}

/**
 * 获取当前用户的完整 HR 档案信息
 *
 * 调用 https://apps.habby.com/api/hr-system/employees/me 接口
 * 包含所有字段：基本信息、组织信息、敏感信息等
 *
 * 本地开发：自动使用 mock 数据
 * 生产环境：调用真实 API
 */
export function useHrInfo() {
  const { data, loading, error, refetch } = useApi<HrApiResponse>(
    'hr-system',
    '/employees/me'
  );

  return {
    data: data?.data || null,
    loading,
    error,
    refetch,
  };
}
