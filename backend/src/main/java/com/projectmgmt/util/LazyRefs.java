package com.projectmgmt.util;

import jakarta.persistence.EntityNotFoundException;
import org.hibernate.Hibernate;

/**
 * Tiện ích xử lý quan hệ lazy (@ManyToOne) có thể trỏ tới bản ghi đã bị xoá
 * (tham chiếu khoá ngoại "treo" do dữ liệu bị import lỗi trước đây).
 *
 * Với proxy lazy của Hibernate, {@code entity.getRelated()} trả về một proxy KHÁC null,
 * nhưng lần đầu truy cập thuộc tính (vd {@code .getCode()}) sẽ ném
 * {@link EntityNotFoundException} nếu bản ghi đích không còn tồn tại — làm sập cả request.
 * {@link #load(Object)} ép khởi tạo proxy và trả về {@code null} thay vì ném lỗi,
 * để một dòng dữ liệu hỏng không làm hỏng cả danh sách.
 */
public final class LazyRefs {

    private LazyRefs() {}

    /**
     * Khởi tạo an toàn một quan hệ lazy.
     * @return chính entity nếu hợp lệ, hoặc {@code null} nếu là null / trỏ tới bản ghi đã mất.
     */
    public static <T> T load(T proxy) {
        if (proxy == null) return null;
        try {
            Hibernate.initialize(proxy);
            return proxy;
        } catch (EntityNotFoundException | org.hibernate.ObjectNotFoundException e) {
            return null;
        }
    }
}
