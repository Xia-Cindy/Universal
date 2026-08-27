export default function RoomBoot() {
    return (
        <main className="room-boot" aria-busy="true" aria-label="Universe Room 正在加载">
            <div className="room-boot__orbit" aria-hidden="true">
                <i />
                <i />
                <i />
            </div>
            <section className="room-boot__content">
                <span>UNIVERSE OS</span>
                <h1>Opening your room</h1>
                <p>房间预览已显示，3D 交互正在后台启动</p>
            </section>
        </main>
    );
}
