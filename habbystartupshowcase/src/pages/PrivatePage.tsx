import { useCurrentUser } from '../hooks/useCurrentUser';
import { useHrInfo } from '../hooks/useHrInfo';
import { config } from '../config';
import './PrivatePage.css';

/**
 * 私人页面组件
 *
 * 🔐 安全保护机制：
 * 1. SSO 登录验证：未登录用户无法访问
 * 2. 创建者身份验证：只有 config.OWNER_EMAIL 匹配的用户才能访问
 * 3. HR API 验证：后端根据 Cookie 返回当前用户的数据
 *
 * ⚠️ 重要：这个页面用于展示敏感的个人 HR 信息，必须确保：
 * - src/config.ts 中的 OWNER_EMAIL 已修改为创建者本人的邮箱
 * - 这是保护私人页面的关键，不是可选配置！
 */
export function PrivatePage() {
  const { user, loading: userLoading } = useCurrentUser();
  const { data: hrInfo, loading: hrLoading, error: hrError } = useHrInfo();

  if (userLoading || hrLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container error">
        <h2>未登录</h2>
        <p>请先登录查看您的信息</p>
      </div>
    );
  }

  // 🔐 创建者身份验证：只有创建者本人才能访问私人页面
  if (user.email !== config.OWNER_EMAIL) {
    return (
      <div className="container error">
        <h2>无权访问</h2>
        <p>此页面仅限创建者本人访问</p>
        <p className="hint">当前登录用户：{user.email}</p>
      </div>
    );
  }

  if (hrError) {
    return (
      <div className="container error">
        <h2>获取信息失败</h2>
        <p>{hrError.message}</p>
      </div>
    );
  }

  if (!hrInfo) {
    return (
      <div className="container error">
        <h2>未找到 HR 信息</h2>
        <p>您的员工档案可能尚未录入系统</p>
      </div>
    );
  }

  return (
    <div className="container private-page">
      <header>
        <h1>我的 HR 档案</h1>
        <p className="subtitle">仅您本人可见 · 包含敏感信息</p>
      </header>

      {/* 基本信息 */}
      <section className="info-section">
        <h2>基本信息</h2>
        <div className="info-grid">
          <div className="info-item">
            <label>员工号</label>
            <span>{hrInfo.employeeId}</span>
          </div>
          <div className="info-item">
            <label>姓名</label>
            <span>{hrInfo.name}</span>
          </div>
          {hrInfo.gender && (
            <div className="info-item">
              <label>性别</label>
              <span>{hrInfo.gender}</span>
            </div>
          )}
          {hrInfo.age && (
            <div className="info-item">
              <label>年龄</label>
              <span>{hrInfo.age} 岁</span>
            </div>
          )}
          {hrInfo.birthDate && (
            <div className="info-item">
              <label>出生日期</label>
              <span>{hrInfo.birthDate}</span>
            </div>
          )}
          {hrInfo.education && (
            <div className="info-item">
              <label>学历</label>
              <span>{hrInfo.education}</span>
            </div>
          )}
          {hrInfo.school && (
            <div className="info-item">
              <label>毕业院校</label>
              <span>{hrInfo.school}</span>
            </div>
          )}
        </div>
      </section>

      {/* 组织信息 */}
      <section className="info-section">
        <h2>组织信息</h2>
        <div className="info-grid">
          {hrInfo.company && (
            <div className="info-item">
              <label>公司</label>
              <span>{hrInfo.company}</span>
            </div>
          )}
          {hrInfo.board && (
            <div className="info-item">
              <label>事业部</label>
              <span>{hrInfo.board}</span>
            </div>
          )}
          <div className="info-item">
            <label>部门</label>
            <span>{hrInfo.department}</span>
          </div>
          <div className="info-item">
            <label>岗位</label>
            <span>{hrInfo.position}</span>
          </div>
        </div>
      </section>

      {/* 工作状态 */}
      <section className="info-section">
        <h2>工作状态</h2>
        <div className="info-grid">
          <div className="info-item">
            <label>入职日期</label>
            <span>{hrInfo.joinDate}</span>
          </div>
          <div className="info-item">
            <label>状态</label>
            <span className={`status ${hrInfo.status}`}>
              {hrInfo.status === 'active' ? '在职' : '离职'}
            </span>
          </div>
          {hrInfo.serviceType && (
            <div className="info-item">
              <label>服务类型</label>
              <span>{hrInfo.serviceType}</span>
            </div>
          )}
          {hrInfo.isProbation !== undefined && (
            <div className="info-item">
              <label>试用期状态</label>
              <span>{hrInfo.isProbation ? '试用期中' : '已转正'}</span>
            </div>
          )}
          {hrInfo.probationEndDate && (
            <div className="info-item">
              <label>试用期结束日期</label>
              <span>{hrInfo.probationEndDate}</span>
            </div>
          )}
        </div>
      </section>

      {/* 联系方式 */}
      <section className="info-section">
        <h2>联系方式</h2>
        <div className="info-grid">
          <div className="info-item">
            <label>工作邮箱</label>
            <span>{hrInfo.workEmail}</span>
          </div>
          {hrInfo.phone && (
            <div className="info-item">
              <label>手机号</label>
              <span>{hrInfo.phone}</span>
            </div>
          )}
          {hrInfo.homeAddress && (
            <div className="info-item full-width">
              <label>家庭地址</label>
              <span>{hrInfo.homeAddress}</span>
            </div>
          )}
          {hrInfo.currentAddress && hrInfo.currentAddress !== hrInfo.homeAddress && (
            <div className="info-item full-width">
              <label>现居地址</label>
              <span>{hrInfo.currentAddress}</span>
            </div>
          )}
          {hrInfo.registeredAddress && (
            <div className="info-item full-width">
              <label>户籍地址</label>
              <span>{hrInfo.registeredAddress}</span>
            </div>
          )}
        </div>
      </section>

      {/* 紧急联系人 */}
      {(hrInfo.emergencyContact || hrInfo.emergencyPhone || hrInfo.emergencyContactPhone) && (
        <section className="info-section">
          <h2>紧急联系人</h2>
          <div className="info-grid">
            {hrInfo.emergencyContact && (
              <div className="info-item">
                <label>联系人</label>
                <span>{hrInfo.emergencyContact}</span>
              </div>
            )}
            {(hrInfo.emergencyPhone || hrInfo.emergencyContactPhone) && (
              <div className="info-item">
                <label>联系电话</label>
                <span>{hrInfo.emergencyPhone || hrInfo.emergencyContactPhone}</span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 敏感信息 */}
      {(hrInfo.idNumber || hrInfo.bankAccount) && (
        <section className="info-section sensitive">
          <h2>敏感信息 <span className="badge">敏感信息</span></h2>
          <div className="info-grid">
            {hrInfo.idType && hrInfo.idNumber && (
              <>
                <div className="info-item">
                  <label>证件类型</label>
                  <span>{hrInfo.idType}</span>
                </div>
                <div className="info-item">
                  <label>证件号码</label>
                  <span>{hrInfo.idNumber}</span>
                </div>
              </>
            )}
            {hrInfo.bankName && (
              <div className="info-item">
                <label>开户行</label>
                <span>{hrInfo.bankName}</span>
              </div>
            )}
            {hrInfo.bankAccount && (
              <div className="info-item">
                <label>银行卡号</label>
                <span>{hrInfo.bankAccount}</span>
              </div>
            )}
          </div>
        </section>
      )}

      <footer>
        <p className="warning">
          ⚠️ 以上信息为敏感个人数据，请勿分享给他人
        </p>
        {hrInfo.updatedAt && (
          <p className="meta">
            最后更新时间：{new Date(hrInfo.updatedAt).toLocaleString('zh-CN')}
          </p>
        )}
      </footer>
    </div>
  );
}
