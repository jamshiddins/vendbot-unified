import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { format } from 'date-fns';
import { operationService } from '../services/operationService';

export const OperationsList: React.FC = () => {
  const { data: operations, isLoading, error } = useQuery({
    queryKey: ['operations'],
    queryFn: () => operationService.getOperations(),
    refetchInterval: 30000 // Обновляем каждые 30 секунд
  });

  if (isLoading) return <CircularProgress />;
  if (error) return <Alert severity="error">Ошибка загрузки операций</Alert>;

  const getOperationTypeColor = (type: string) => {
    switch (type) {
      case 'fill': return 'primary';
      case 'install': return 'success';
      case 'remove': return 'warning';
      case 'clean': return 'info';
      default: return 'default';
    }
  };

  const getOperationTypeLabel = (type: string) => {
    switch (type) {
      case 'fill': return 'Заполнение';
      case 'install': return 'Установка';
      case 'remove': return 'Снятие';
      case 'clean': return 'Чистка';
      default: return type;
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Тип</TableCell>
            <TableCell>Бункер</TableCell>
            <TableCell>Ингредиент</TableCell>
            <TableCell>Кол-во до</TableCell>
            <TableCell>Добавлено</TableCell>
            <TableCell>Кол-во после</TableCell>
            <TableCell>Оператор</TableCell>
            <TableCell>Время</TableCell>
            <TableCell>Синхронизация</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {operations?.map((operation) => (
            <TableRow key={operation.id}>
              <TableCell>{operation.id}</TableCell>
              <TableCell>
                <Chip
                  label={getOperationTypeLabel(operation.operation_type)}
                  color={getOperationTypeColor(operation.operation_type)}
                  size="small"
                />
              </TableCell>
              <TableCell>{operation.hopper_id}</TableCell>
              <TableCell>{operation.ingredient_id || '-'}</TableCell>
              <TableCell>{operation.quantity_before?.toFixed(2) || '-'}</TableCell>
              <TableCell>{operation.quantity_added?.toFixed(2) || '-'}</TableCell>
              <TableCell>{operation.quantity_after?.toFixed(2) || '-'}</TableCell>
              <TableCell>{operation.operator_id}</TableCell>
              <TableCell>
                {format(new Date(operation.created_at), 'dd.MM.yyyy HH:mm')}
              </TableCell>
              <TableCell>
                <div style={{ display: 'flex', gap: 4 }}>
                  {operation.sync_status.telegram && <Chip label="TG" size="small" color="success" />}
                  {operation.sync_status.web && <Chip label="Web" size="small" color="success" />}
                  {operation.sync_status.mobile && <Chip label="Mob" size="small" color="success" />}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};