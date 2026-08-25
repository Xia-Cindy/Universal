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
                <h1>Preparing your room</h1>
                <p>正在装载个人空间与交互场景</p>
            </section>
        </main>
    );
}
