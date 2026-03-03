import './PublicPage.css';

export function PublicPage() {
  return (
    <div className="layout-wrapper">
      <div className="layout-content">
        <header className="header">
          <div className="brand">hz</div>
          <nav className="nav-links">
            <a href="#about">关于</a>
            <a href="#projects">领域</a>
            <a href="#contact">联系</a>
          </nav>
        </header>

        <main className="main">
          <section className="hero-section">
            <h1 className="hero-title">
              你好，我是衡孜涵。<br/>
              <span className="text-gray">一名专注于设计与交互的</span><br/>
              <span className="text-black">前端工程师。</span>
            </h1>
            <p className="hero-subtitle">
              现居北京，就职于 Habby，致力于打造极简、优雅的数字体验。
            </p>
          </section>

          <section id="about" className="section">
            <h2 className="section-title">01 / 关于</h2>
            <div className="section-content">
              <p>
                我相信少即是多（Less is more）。在代码与设计的交汇处，我追求极致的克制与恰到好处的表达。每一次敲击键盘，都是为了让世界变得更简单一点点。
              </p>
            </div>
          </section>

          <section id="projects" className="section">
            <h2 className="section-title">02 / 领域</h2>
            <div className="section-content grid-2">
              <div className="card">
                <h3>前端工程化</h3>
                <p>构建稳定、可扩展的现代 Web 应用程序基础设施。</p>
              </div>
              <div className="card">
                <h3>UI/UX 设计</h3>
                <p>通过像素级的细节把控，创造直觉般的用户体验。</p>
              </div>
            </div>
          </section>

          <section id="contact" className="section">
            <h2 className="section-title">03 / 联系</h2>
            <div className="section-content flex-gap">
              <a href="mailto:hengzihan@habby.com" className="link-button">Email ↗</a>
              <a href="https://github.com/hengzihan" className="link-button" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
            </div>
          </section>
        </main>

        <footer className="footer">
          <p>© 2026 hengzihan.</p>
        </footer>
      </div>
    </div>
  );
}